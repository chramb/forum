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
select comments_get(2);
