-- Crete Post

select * from post;

create or replace function tag_get_id(tag_name varchar(64))
    returns bigint
    language plpgsql
as $$
declare tag_id bigint;
begin
    select tag.id from tag where tag.name = tag_name into  tag_id;
    return tag_id;
end$$;

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

select a.uid from account a where a.username = 'u1';
call post_create(
    author_uid := 'f280aa75-f1ca-46ee-96fb-409aa9e65670',
    title := 'Hello, World!',
    content := 'My first post on this forum, @u1',
    tag := 'test'
    );
