select a.username,
       a.time_created::date as date_created,
       array_agg(r.title) as role
from account a
left join account_role ar on a.uid = ar.account_uid
left join role r on ar.role_id = r.id
where a.username = 'u2' -- '%(username)s'
group by a.username, date_created