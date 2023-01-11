---- Helper Functions
-- TODO: use view to restrict access to passwords
/*
create or replace function json_user_get(username varchar(32))
    returns json
    language plpgsql
as
$$
declare
    uid usr_json;
begin
    select account.uid, account.username, account.
    into uid
    from account
    where account.username = json_user_get.username;
    return uid;
end;
$$;

*/