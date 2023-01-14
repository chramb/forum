create or replace function comment_get_recursive_json_v1(id bigint)
    returns json
    language plpgsql
as $$ declare output json;
begin
    select json_build_object(
                   'id', c.id,
                   'message', c.msg,
                   'author', json_build_object(
                           'uid', c.creator_uid,
                           'username', (select a.username from account a where a.uid = c.creator_uid)),
                   'creation_time', date_trunc('seconds', c.creation_date),
                   'edited', (select c.last_update is not null),
                   'score', c.score,
                   'responses', coalesce((select json_agg(comment_get_recursive_json_v1(response.id))
                                          from comment as response
                                          where response.response_for = c.id
                                             -- order by r.score
                                         ), '[]'))
    from comment c
    where c.id = comment_get_recursive_json_v1.id
    into output;

    return output;
end $$;
create or replace function comment_get_recursive_json_v0(id bigint)
    returns json
    language plpgsql
as
$$
declare
    output json;
begin
    select json_agg(q)
    from (select c.id,
                 json_build_object(
                         'uid', c.creator_uid,
                         'username', (select a.username from account a where a.uid = c.creator_uid)
                     )                                          as author,
                 date_trunc('seconds', c.creation_date)         as creation_time,
                 (select c.last_update is not null)             as edited,
                 c.score,
                 --array (select c2.id from comment c2 where c2.response_for = c.id)
                 --    as responses
                 coalesce((select json_agg(comment_get_recursive_json_v0(c2.id))
                           from comment c2
                           where c2.response_for = c.id), '[]') as responses

          from comment c
          where c.id = comment_get_recursive_json_v0.id)
             as q
    into output;

    return output;
end
$$;
create or replace function comment_get(id bigint)
    returns json
    language plpgsql
as
$$
begin
    return (select c.id,
                   json_build_object(
                           'uid', c.creator_uid,
                           'username', (select a.username from account a where a.uid = c.creator_uid)
                       )                                                            as author,
                   date_trunc('seconds', c.creation_date)                           as creation_time,
                   (select c.last_update is not null)                               as edited,
                   c.score,
                   array(select c2.id from comment c2 where c2.response_for = c.id) as responses

            from comment c
            where c.id = comment_get.id);

end
$$;



create or replace function comment_get_recursive_json_v2(id bigint)
    returns json
    language plpgsql
as $$ declare output json;
begin
    select json_build_object(
                   'id', c.id,
                   'message', c.msg,
                   'author', json_build_object(
                           'uid', c.creator_uid,
                           'username', (select a.username from account a where a.uid = c.creator_uid)),
                   'creation_time', date_trunc('seconds', c.creation_date),
                   'edited', c.last_update is not null,
                   'score', c.score,
                   'responses', coalesce((select json_agg(comment_get_recursive_json_v2(response.id))
                                          from comment as response
                                          where response.response_for = c.id
                                             -- order by r.score
                                         ), '[]'))
    from comment c
    where c.id = comment_get_recursive_json_v2.id
    into output;

    return output;
end $$;
select comment_get_recursive_json_v2(1);


select *
from comment;
/*
# Dokumentacja:

- Co to za projekt
- O czym

- Przypadki użycia
- Najciekawsze zapytania
- Sposób uruchomienia


# Prezentacja:
- Co zrobiliśmy
- Jaka architektura
- Prezentacja

# 2 rzeczy:
- Co się udało, nie udało
- Czego się nauczyliśmy
*/
