select * from post;

select json_build_object(
    'id', p.id,
    'title', p.title,
    'author', json_build_object(
        'uid',p.creator_uid,
        'username',a.username -- or subquery here?
        ),
    'edited', p.last_update is not null,
    'comments', json_agg(comment_get_recursive_json_v1(c.id))
           ) as post from post as p
join account a on a.uid = p.creator_uid -- join here?
left join comment c on c.post_id = p.id
group by p.id, a.username; -- TODO: FIX THIS missing 'my first post' twice 'hello fellow'
