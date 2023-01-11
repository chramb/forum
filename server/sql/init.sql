create extension if not exists  "uuid-ossp"; -- enable uuid extension
-- select "name","installed_version" from pg_available_extensions where "name"='uuid-ossp';
-- select uuid_generate_v4()

create table if not exists role
(
    id    serial primary key,
    title varchar(32)
);
insert into role (title) values ('admin');
insert into role (title) values ('moderator');
insert into role (title) values ('user');

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

create table if not exists account
(
    uid      uuid primary key,
    time_created timestamp default now(),
    username varchar(32) unique  not null,
    password varchar(128)        not null,
    email    varchar(128) unique not null
);
create table if not exists tag
(
    tag varchar(64) primary key
);
create table if not exists post -- phone
(
    id            bigserial primary key,
    creation_date timestamp default now(), -- brand int references brand(brand_id),
    last_update   timestamp default null,
    title         varchar(32) not null,
    creator_uid   uuid references account (uid),
    tag           varchar(64) references tag (tag),
    unique (title, creator_uid)
    -- probably should replace with timestamp check (eg. < 5 Minutes: can't create post with same (title, creator_uid))
);

create table if not exists comment
(
    id            bigserial primary key,
    creator_uid   uuid references account (uid), -- TODO: null if user is deleted deletes (cascade do stuff)
    post_id       int references post (id) not null,
    creation_date timestamp default now(),
    last_update   timestamp default null,
    response_for  bigint references comment(id) default null,
    msg           varchar(1024),
    score         int  default 0,                -- TODO: update with trigger
    unique (id, response_for)                    -- Can't respond to himself
);

create table if not exists follow_tag
(
    account_uid uuid references account (uid),
    tag         varchar(64) references tag (tag),
    primary key (account_uid, tag)
);
create table if not exists account_role (
  account_uid uuid references account(uid),
  role_id int references role(id),
  primary key (account_uid, role_id)
);
create table if not exists follow_account
(
    subscriber uuid references account (uid),
    followed   uuid references account (uid),
    unique (subscriber, followed),
    primary key (subscriber, followed)
);
create table if not exists upvote -- TODO: function for adding and removing if already exist
(
    comment_id  int references "comment" (id) not null,
    account_uid uuid references account (uid) not null
);

