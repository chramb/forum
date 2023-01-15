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

call post_update(
    author_uid := '8be04cdc-fc4b-492d-b540-c75cee494a98',
    post_id := 7,
    title := 'Testing update #1',
    tag := 'yolo',
    content := 'if you see this message, procedure worked'
)