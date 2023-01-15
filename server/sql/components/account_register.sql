create or replace procedure assign_account_role_by_name(
        account_username varchar(32),
        role_title varchar(32)
    )
    language plpgsql
as $$begin
    insert into account_role(account_uid, role_id)
    values (
               (select account.uid from account where account.username = account_username),
               (select role.id from role where role.title = role_title)
           );
end$$;

create or replace procedure assign_account_role(
    account_uid uuid,
    role_id int
)
    language plpgsql
as $$begin
    insert into account_role(account_uid, role_id)
    values (assign_account_role.account_uid,
            assign_account_role.role_id);
end$$;

create or replace function role_get_id_from_title(
    role_title varchar(32)
)
    returns int
    language plpgsql
as $$
    declare r_id varchar(32);
begin
    select role.id from role
        where role.title = role_get_id_from_title.role_title
        into r_id;
    return r_id;
end$$;

create or replace procedure account_register(
        username varchar(32),
        password varchar(128),
        email varchar(128)
    )
language plpgsql
as $$
    declare
        acc_uid uuid;
    begin
    -- create user
    select uuid_generate_v4() into acc_uid;

    insert into account (uid, username, password, email)
    values (acc_uid,
            account_register.username,
            account_register.password,
            account_register.email);

    -- perform because return is void so we don't care about result
    call assign_account_role(acc_uid,role_get_id_from_title('user'));

end $$;

--- Test Create users
call account_register( 'u1','pass','u1@example.com');
call account_register('u2','pass','u2@example.com');
call account_register( 'u3','secret', 'u3@example.com');
call account_register( 'u4','secret', 'u4@example.com');
call account_register( 'u5','secret', 'u5@example.com');
call assign_account_role_by_name('u1','admin');
call assign_account_role_by_name('u2','moderator');

-- tests
/*
insert into account (uid, username, password, email)
values (uuid_generate_v4(), 'u2', 'pass', 'u2@example.com');
*/

--- Show all users with all roles
/*
select account.username, role.title from account
left join account_role on account.uid = account_role.account_uid
left join role on account_role.role_id = role.id;

select account.username, role.title from account_role
left join account on account_role.account_uid = account.uid
join role on account_role.role_id = role.id;
--*/
