select * from post;
-- TODO: create post
-- TODO: View post
-- TODO: update post
-- TODO: comment
/* TODO:
 * -------------------------------
 * [X] create single comment
 * create 2nd comment
 *   create response
 *     create response to response
 * create 3rd comment
 * create 4th comment
 *   create response
 * -------------------------------
 * make function/procedure that'll return json/dict
 * with nested responses and sorted by creation date
 *
 * sort inside comment_get() function to get them in proper order
 */

create or replace procedure comment_post(
        creator_uid uuid,
        post_id bigint,
        msg varchar(1024),
        respond_to bigint default null
    )
    language plpgsql
as $$begin
    insert into comment (creator_uid, post_id, response_for, msg)
    values (
        comment_post.creator_uid,
        comment_post.post_id,
        comment_post.respond_to,
        comment_post.msg
    );
end$$;

select * from comment;
select * from account;
select * from post;
-- respond to post
call comment_post(
    creator_uid := 'b2016300-d954-4d12-867d-9c74f3fc9d3b',
    post_id := 5,
    msg := 'Hello Mate :D',
    respond_to := 1
);
-- op responds to response
call comment_post(
    creator_uid := 'f280aa75-f1ca-46ee-96fb-409aa9e65670',
    post_id := 5, msg := 'Hi fellow comment section user.',
    respond_to := 2
);
-- 3rd guy comments
call comment_post(
        creator_uid := '1bf36366-f4c2-4582-a0e2-4dab4e7fe89e',
        post_id := 5,
        msg := 'Blah Bl...',
        respond_to := 1
    );
call comment_post(
        creator_uid := '1bf36366-f4c2-4582-a0e2-4dab4e7fe89e',
        post_id := 5,
        msg := '..ah Blah!',
        respond_to := 6
    );

