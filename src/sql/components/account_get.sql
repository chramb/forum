select a.username, array_agg(r.title) as role
--       account.time_created::date as date_created
from account a
left join account_role ar on a.uid = ar.account_uid
left join role r on ar.role_id = r.id
--where %(column_name)s = %(val)s
group by a.username;




select *
--       account.time_created::date as date_created
from account
         left join account_role ar on account.uid = ar.account_uid
         left join role r on ar.role_id = r.id;
--where %(column_name)s = %(val)s
