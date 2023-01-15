-- enable UUID extension
-- adds `select uuid_generate_v4()`
create extension if not exists "uuid-ossp";

-- role table
create table if not exists role
(
    id    serial primary key,
    title varchar(32)
);
-- add needed roles
insert into role (title) values ('user');
insert into role (title) values ('admin');
insert into role (title) values ('moderator');

-- get id of role(user)
create or replace function user_role_id()
    -- function created because 'default' cant take subquery
    returns int
    language plpgsql
as
$$
declare
    usr_r_id int;
begin
    select role.id
    into usr_r_id
    from role
    where role.title = 'user';
    return usr_r_id;
end
$$;

--- rest of the tables

-- account table
create table if not exists account
(
    uid          uuid primary key,
    time_created timestamp default now(),
    username     varchar(32) unique  not null,
    password     varchar(128)        not null,
    email        varchar(128) unique not null
);

-- tag table
create table if not exists tag
(
    id bigserial  primary key,
    name varchar(64) not null unique
);

-- post table
create table if not exists post -- phone
(
    id            bigserial primary key,
    creation_date timestamp default now(), -- brand int references brand(brand_id),
    last_update   timestamp default null,
    title         varchar(32) not null,
    creator_uid   uuid references account (uid) on delete set null,
    tag_id        bigint references tag (id),
    unique (title, creator_uid)
    -- probably should replace with timestamp check (eg. < 5 Minutes: can't create post with same (title, creator_uid))
);

--- comment table
create table if not exists comment
(
    id            bigserial primary key,
    creator_uid   uuid references account (uid) on delete set null,            -- TODO: null if user is deleted deletes (cascade do stuff)
    post_id       int references post (id) on delete cascade not null,
    creation_date timestamp                      default now(),
    last_update   timestamp                      default null,
    response_for  bigint references comment (id) default null,
    msg           varchar(1024),
    score         int                            default 0, -- TODO: update with trigger
    unique (id, response_for)                               -- Can't respond to himself
);

--- references (many-many) relation

-- follow tag (phone)
create table if not exists follow_tag
(
    account_uid uuid references account (uid),
    tag         bigint references tag (id),
    primary key (account_uid, tag)
);

-- account role (admin, user, etc)
create table if not exists account_role
(
    account_uid uuid references account (uid),
    role_id     int references role (id),
    primary key (account_uid, role_id)
);

-- follow account (change to brand)
create table if not exists follow_account
(
    subscriber uuid references account (uid),
    followed   uuid references account (uid),
    unique (subscriber, followed),
    primary key (subscriber, followed)
);

-- create upvote table -- TODO: do something with it or remove it completely
create table if not exists upvote -- TODO: function for adding and removing if already exist
(
    comment_id  int references "comment" (id) not null,
    account_uid uuid references account (uid) not null
);


---- functions and procedures

--- account

-- assign role by role.title
create or replace procedure assign_account_role_by_name(
    account_username varchar(32),
    role_title varchar(32)
)
    language plpgsql
as $$begin
    insert into account_role(account_uid, role_id)
    values (
               (select account.uid from account where account.username = account_username),
               (select role.id from role where role.title = role_title)
           );
end$$;

-- assign account role by role.id
create or replace procedure assign_account_role(
    account_uid uuid,
    role_id int
)
    language plpgsql
as $$begin
    insert into account_role(account_uid, role_id)
    values (assign_account_role.account_uid,
            assign_account_role.role_id);
end$$;

-- get role.id from role.title
create or replace function role_get_id_from_title(
    role_title varchar(32)
)
    returns int
    language plpgsql
as $$
declare r_id varchar(32);
begin
    select role.id from role
    where role.title = role_get_id_from_title.role_title
    into r_id;
    return r_id;
end$$;

-- register account
create or replace procedure account_register(
    username varchar(32),
    password varchar(128),
    email varchar(128)
)
    language plpgsql
as $$
declare
    acc_uid uuid;
begin
    -- create user
    select uuid_generate_v4() into acc_uid;

    insert into account (uid, username, password, email)
    values (acc_uid,
            account_register.username,
            account_register.password,
            account_register.email);

    -- perform because return is void so we don't care about result
    call assign_account_role(acc_uid,role_get_id_from_title('user'));

end $$;

--- comment

-- get comment in json
create or replace function comment_get(id bigint)
    returns json
    language plpgsql
as $$ declare output json;
begin
    select json_build_object(
                   'comment_id', c.id,
                   'message', c.msg,
                   'author', json_build_object(
                           'uid', c.creator_uid,
                           'username', (select a.username from account a where a.uid = c.creator_uid)),
                   'creation_time', c.creation_date, --date_trunc('seconds', c.creation_date),
                   'edited', c.last_update is not null,
                   'score', c.score,
                   'responses', coalesce((select json_agg(comments_get(response.id))
                                          from comment as response
                                          where response.response_for = c.id
                                             -- order by r.score
                                         ), '[]'))
    from comment c
    where c.id = comment_get.id
    into output;

    return output;
end $$;


--- tag

-- get tag.id from name
create or replace function tag_get_id(tag_name varchar(64))
    returns bigint
    language plpgsql
as $$
declare tag_id bigint;
begin
    select tag.id from tag where tag.name = tag_name into  tag_id;
    return tag_id;
end$$;


--- post

-- create post
create or replace procedure post_create(
    author_uid uuid,
    title varchar(32),
    tag varchar(32),
    content varchar(1024)
)
    language plpgsql
as $$begin
    -- check if null when creating
    -- (can't be null when creating but can after deleting user [deleted])
    if author_uid is null then
        raise NULL_VALUE_NOT_ALLOWED;
    end if;
    -- Create tag if doesn't exist
    insert into tag(name)
    values (post_create.tag)
    on conflict do nothing;
    -- Create Post
    insert into post (title, creator_uid, tag_id)
    values (title, author_uid, tag_get_id(post_create.tag));
    -- First Comment (Post content) -- remove on phone impl
    insert into "comment" (msg, post_id, creator_uid)
    values ("content",
            (select post.id
             from post
             where post.title = post_create.title
               and creator_uid = author_uid),
            author_uid);
end$$;

-- update post
create or replace procedure post_update(
    author_uid uuid,
    post_id bigint,
    title varchar(32),
    tag varchar(32),
    content varchar(1024)
)
    language plpgsql
as $$begin
    -- check if null when creating
    -- (can't be null when creating but can after deleting user [deleted])
    if author_uid is null then
        raise NULL_VALUE_NOT_ALLOWED;
    end if;
    -- Create tag if doesn't exist
    insert into tag(name)
    values (post_update.tag)
    on conflict do nothing;
    -- Update Post
    update post p
    set
        last_update = now(),
        title = post_update.title,
        tag_id = tag_get_id(post_update.tag)
    where post_update.post_id = p.id and post_update.author_uid = p.creator_uid;
    -- First Comment (Post content) -- remove on phone impl
    update comment c
    set
        last_update = now(),
        msg = post_update.content
    where
        c.response_for is null
      and c.post_id = post_update.post_id
      and c.creator_uid = post_update.author_uid;

end$$;
