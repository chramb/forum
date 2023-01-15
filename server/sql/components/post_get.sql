select json_build_object(
    'id', p.id,
    'title', p.title,
    'author', json_build_object(
        'uid',p.creator_uid,
        'username',a.username -- or subquery here?
        ),
    'edited', p.last_update is not null,
    'comments', json_agg(comment_get(c.id))
           ) as post
from post as p
    join account a on a.uid = p.creator_uid-- join here?
    join comment c on c.post_id = p.id
group by p.id, a.username; -- TODO: FIX THIS missing 'my first post' twice 'hello fellow'

select
    p.id,
    json_build_object(
        'uid', p.creator_uid,
        'username', a.username
        ) as author,
    p.title,
    json_agg(comment_get(c.id))
from post p
         join account a on a.uid = p.creator_uid
         join comment c on p.id = c.post_id where response_for is null
group by p.id, a.username, p.title, c.creation_date, c.score order by c.creation_date, c.score;


/*
select
    p.id,
    json_build_object(
            'uid', p.creator_uid,
            'username', a.username
        ) as author,
    p.title,
    p.creation_date,
    p.last_update is null as edited,
    json_agg(comment_get_recursive_json_v2(c.id))
from post p
    join account a on a.uid = p.creator_uid
    join comment c on p.id = c.post_id
    where c.response_for is null
        and p.id = %s
group by p.id, a.username, p.title, c.creation_date, c.score order by c.creation_date, c.score
