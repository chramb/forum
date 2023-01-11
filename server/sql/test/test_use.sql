/*
Use:
1. Create two users
2. One posts something w/ tags
3. the other comments on post
TODO: add tags?
TODO: full text search (comments|post-titles|post content[title+1st comment])
TODO: backend
*/
---- Helper Functions
create or replace function uuid_from_name(_username varchar(32))
    returns uuid
    language plpgsql
as
$$
declare
    uid uuid;
begin
    select account.uid
    into uid
    from account
    where account.username = _username;
    return uid;
end;
$$;

---- Create users
insert into account (uid, username, password, email)
values (uuid_generate_v4(), 'u1', 'pass', 'u1@example.com');
insert into account (uid, username, password, email)
values (uuid_generate_v4(), 'u2', 'pass', 'u2@example.com');

---- User (u1) creates post
-- TODO: fix content input (unused var)
create procedure create_post(user_uid uuid, title varchar(32), content varchar(1024))
    language plpgsql
as
$$
begin
    insert into post (title, creator_uid)
    values (title, user_uid);
    insert into "comment" (msg, post_id, creator_uid)
    values ("content",
            (select post_id
             from post
             where post.title = create_post.title
               and creator_uid = user_uid),
            user_uid);
-- check if null when creating (can't be null when creating but can after deleting user
end;
$$;

call create_post(uuid_from_name('u1'),
                 'Hello, World!',
                 'My first post here :)');

---- User (u2) comments
insert into "comment" (content, post_id, creator_uid)
values ('Hi dude',
        (select post_id
         from post
         where post_title = 'Hello, World!'
           and creator_uid = uuid_from_name('u1')),
        uuid_from_name('u2'));
---- User (u1) upvotes (u2's) comment
insert into upvote (comment_id, account_uid)
values ((select comment_id from comment where "content" = 'My first post here :)'), uuid_from_name('u1'));

---- See all upvotes of user (with comment contents)
-- TODO: turn into view
-- TODO: create stats view for user
select distinct c.comment_id, account_username, c.content from upvote
left join comment c on c.comment_id = upvote.comment_id
left join account a on a.account_uid = upvote.account_uid
where account_username = 'u1';
-- TODO: notifications (dissmisable) table pg_notify

---- u2 creates post
call create_post(uuid_from_name('u2'),
                 'Testing post features',
                 'This is some conten blah blah blah'
    );


---- return post as json
create function get_post(p_post_id int)
    returns json
    language plpgsql
as
$$
declare
    post_json json;
begin
    select json_build_object(
                   'post_id', t.post_id,
                   'title', t.post_title,
                   'creator_username', t.account_username,
                   'comments', (select json_agg(q) as comments
                                from (select comment_id, account_username, content, score
                                      from comment
                                               left join account a on comment.creator_uid = a.account_uid
                                      where comment.post_id = p_post_id
                                      order by comment_id)
                                         as q)
               ) as "post"
    from (select post.post_id, post.post_title, a2.account_username
          from post
                   left join account a2 on post.creator_uid = a2.account_uid
          where post.post_id = p_post_id) as t
    into post_json;
    return post_json;
end;
$$;
