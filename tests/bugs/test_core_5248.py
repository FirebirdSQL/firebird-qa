#coding:utf-8
#
# id:           bugs.core_5248
# title:        Improve consistency in GRANT syntax between roles and privileges according to SQL standard
# decription:   
#                  Checked on 4.0.0.249; 3.0.1.32585
#                
# tracker_id:   CORE-5248
# min_versions: ['3.0.1']
# versions:     3.0.1, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set autoddl off;
    commit;
    connect '$(DSN)' user sysdba password 'masterkey';
    create or alter user tmp$c5248_usr0 password 'c5248$u0';
    create or alter user tmp$c5248_usrx password 'c5248$ux';
    commit;
    grant create role to user tmp$c5248_usr0;
    commit;

    set term ^;
    execute block as
    begin
      execute statement 'drop role test_role1';
      when any do begin end
    end^
    set term ;^
    commit;

    connect '$(DSN)' user tmp$c5248_usr0 password 'c5248$u0';
    create role test_role1; -- tmp$c5248_usr0 is owner of role test_role1
    commit;

    --  drop role - should fail
    connect '$(DSN)' user tmp$c5248_usrx password 'c5248$ux';

    -- Statement failed, SQLSTATE = 28000
    -- unsuccessful metadata update
    -- -DROP ROLE TEST_ROLE1 failed
    -- -no permission for DROP access to ROLE TEST_ROLE1

    drop role test_role1; -- should fail: this user is not owner of this role and he was not granted to use it with admin option
    select count(*) from rdb$roles where rdb$role_name = 'TEST_ROLE1';
    rollback;

    connect '$(DSN)' user sysdba password 'masterkey';
    drop user tmp$c5248_usr0;
    drop user tmp$c5248_usrx;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    COUNT                           1
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -DROP ROLE TEST_ROLE1 failed
    -no permission for DROP access to ROLE TEST_ROLE1
  """

@pytest.mark.version('>=3.0.1,<4.0')
def test_core_5248_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = [('-TMP\\$C5248_USR1 is not grantor of (role|ROLE|Role) on TEST_ROLE1 to TMP\\$C5248_USR1.', '-TMP$C5248_USR1 is not grantor of ROLE on TEST_ROLE1 to TMP$C5248_USR1.'), ('-Effective user is.*', '')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    set list on;
    set count on;
    set autoddl off;
    --set echo on;
    commit;
    connect '$(DSN)' user sysdba password 'masterkey';
    create or alter user tmp$c5248_usr0 password 'c5248$u0';
    create or alter user tmp$c5248_usr1 password 'c5248$u1';
    create or alter user tmp$c5248_usr2 password 'c5248$u2';
    create or alter user tmp$c5248_usr3 password 'c5248$u3';
    create or alter user tmp$c5248_usrx password 'c5248$ux';
    commit;
    grant create role to user tmp$c5248_usr0;
    commit;

    set term ^;
    execute block as
    begin
      execute statement 'drop role test_role1';
      when any do begin end
    end^
    set term ;^
    commit;

    recreate view v_grants as
    select
         current_user                    as who_am_i
        ,p.RDB$USER                      as who_was_granted
        ,p.RDB$PRIVILEGE                 as privilege_type 
        ,p.RDB$RELATION_NAME             as role_name       
        ,r.RDB$OWNER_NAME                as role_owner
        ,p.RDB$GRANTOR                   as granted_by
        ,p.RDB$GRANT_OPTION              as grant_option   
    from rdb$user_privileges p
    left join rdb$roles r on p.rdb$relation_name = r.rdb$role_name
    where p.rdb$object_type=13
    ;
    commit;
    grant select on v_grants to public;
    commit;

    connect '$(DSN)' user tmp$c5248_usr0 password 'c5248$u0';
    create role test_role1; -- tmp$c5248_usr0 is owner of role test_role1
    commit;

    connect '$(DSN)' user sysdba password 'masterkey';
    grant test_role1 to tmp$c5248_usr1 with admin option;
    grant test_role1 to tmp$c5248_usr3;
    commit;

    connect '$(DSN)' user tmp$c5248_usr1 password 'c5248$u1';
    grant test_role1 to tmp$c5248_usr2; ----------------------- tmp$c5248_usr1 grants role to tmp$c5248_usr2
    commit;

    -- 1. revoke - avoid cascade grants delete

    connect '$(DSN)' user sysdba password 'masterkey';

    select * from v_grants where upper(who_was_granted) in ( upper('tmp$c5248_usr1'), upper('tmp$c5248_usr2') );  -- must contain 2 records

    revoke test_role1 from tmp$c5248_usr1; -- Q: whether grant on role 'test_role1' remains to user 'tmp$c5248_usr2' after revoking from 'tmp$c5248_usr1' ?

    select * from v_grants where upper(who_was_granted) in ( upper('tmp$c5248_usr1'), upper('tmp$c5248_usr2') );  -- must contain 1 record for tmp$c5248_usr2

    -- return grant to tmp$c5248_usr1 because it was revoked just now:
    rollback;
    --grant test_role1 to tmp$c5248_usr1 with admin option;
    --commit;



    -- 2. revoke: user who has 'admin option' can revoke role from anyone EXCEPT himself
    connect '$(DSN)' user tmp$c5248_usr1 password 'c5248$u1';

    -- Following REVOKE should fail with:
    -- Statement failed, SQLSTATE = 42000
    -- unsuccessful metadata update
    -- -REVOKE failed
    -- -tmp$c5248_usr1 is not grantor of Role on TEST_ROLE1 to tmp$c5248_usr1.
    revoke test_role1 from tmp$c5248_usr1;

    select * from v_grants where upper(who_was_granted) = upper('tmp$c5248_usr1'); -- record should remain
    rollback;



    -- 3. revoke - check role owner rights
    connect '$(DSN)' user tmp$c5248_usr0 password 'c5248$u0';

    select * from v_grants where upper(who_was_granted) = upper('tmp$c5248_usr3');

    -- current user = tmp$c5248_usr0 - is owner of role test_role1, but this role was granted to tmp$c5248_usr3 by SYSDBA.
    -- Q: should user 'c5248$u0' (current) be able to revoke role which he did NOT grant but owns ?
    -- A: yes.

    revoke test_role1 from tmp$c5248_usr3;  -- NO error/warning should be here

    select * from v_grants where upper(who_was_granted) = upper('tmp$c5248_usr3'); -- record should NOT appear.
    rollback;



    -- 4. revoke - check admin option
    connect '$(DSN)' user tmp$c5248_usr1 password 'c5248$u1';

    select * from v_grants where upper(who_was_granted) in ( upper('tmp$c5248_usr1'), upper('tmp$c5248_usr3') ); -- two records should be here

    -- current user = tmp$c5248_usr1 - is NOT owner of role TEST_ROLE1 but he was granted to use it WITH ADMIN option
    -- (grant test_role1 to tmp$c5248_usr1 with admin option).
    -- Q: should user 'tmp$c5248_usr1' (current) be able to revoke role which he neither did grant nor owns but has admin option ?
    -- A: yes.

    revoke test_role1 from tmp$c5248_usr3;

    select * from v_grants where upper(who_was_granted) in (upper('tmp$c5248_usr1'), upper('tmp$c5248_usr3')); -- only one record should be here
    rollback;


    -- 5a. drop role - should fail
    connect '$(DSN)' user tmp$c5248_usrx password 'c5248$ux';

    -- Statement failed, SQLSTATE = 28000
    -- unsuccessful metadata update
    -- -DROP ROLE TEST_ROLE1 failed
    -- -no permission for DROP access to ROLE TEST_ROLE1

    drop role test_role1; -- should fail: this user is not owner of this role and he was not granted to use it with admin option
    
    set count off;
    select count(*) from rdb$roles where rdb$role_name = 'TEST_ROLE1';
    set count on;
    rollback;

    connect '$(DSN)' user tmp$c5248_usr0 password 'c5248$u0';

    select * from v_grants where upper(role_name) = upper('TEST_ROLE1'); -- should output 3 records

    drop role test_role1; -- current user: 'tmp$c5248_usr0' - is owner of role test_role1

    select * from rdb$roles where upper(rdb$role_name) = upper('TEST_ROLE1'); -- should output 0 records
    select * from v_grants where upper(role_name) = upper('TEST_ROLE1');        -- should output 0 records
    rollback;


    -- 6. drop role - check admin option
    connect '$(DSN)' user tmp$c5248_usr1 password 'c5248$u1';

    -- current user: 'tmp$c5248_usr1' - HAS grant on role TEST_ROLE1 with admin option (but he is NOT owner of this role).

    select * from v_grants where upper(role_name) = upper('TEST_ROLE1'); -- should output 3 records

    drop role test_role1; -- current user: 'tmp$c5248_usr0' - is owner of role test_role1

    select * from rdb$roles where upper(rdb$role_name) = upper('TEST_ROLE1'); -- should output 0 records
    select * from v_grants where upper(role_name) = upper('TEST_ROLE1');        -- should output 0 records
    rollback;


    connect '$(DSN)' user sysdba password 'masterkey';
    drop user tmp$c5248_usr0;
    drop user tmp$c5248_usr1;
    drop user tmp$c5248_usr2;
    drop user tmp$c5248_usr3;
    drop user tmp$c5248_usrx;
    commit;

  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    WHO_AM_I                        SYSDBA
    WHO_WAS_GRANTED                 TMP$C5248_USR1                                                                                                                                                                                                                                              
    PRIVILEGE_TYPE                  M     
    ROLE_NAME                       TEST_ROLE1                                                                                                                                                                                                                                                  
    ROLE_OWNER                      TMP$C5248_USR0                                                                                                                                                                                                                                              
    GRANTED_BY                      SYSDBA                                                                                                                                                                                                                                                      
    GRANT_OPTION                    2

    WHO_AM_I                        SYSDBA
    WHO_WAS_GRANTED                 TMP$C5248_USR2                                                                                                                                                                                                                                              
    PRIVILEGE_TYPE                  M     
    ROLE_NAME                       TEST_ROLE1                                                                                                                                                                                                                                                  
    ROLE_OWNER                      TMP$C5248_USR0                                                                                                                                                                                                                                              
    GRANTED_BY                      TMP$C5248_USR1                                                                                                                                                                                                                                              
    GRANT_OPTION                    0


    Records affected: 2

    WHO_AM_I                        SYSDBA
    WHO_WAS_GRANTED                 TMP$C5248_USR2                                                                                                                                                                                                                                              
    PRIVILEGE_TYPE                  M     
    ROLE_NAME                       TEST_ROLE1                                                                                                                                                                                                                                                  
    ROLE_OWNER                      TMP$C5248_USR0                                                                                                                                                                                                                                              
    GRANTED_BY                      TMP$C5248_USR1                                                                                                                                                                                                                                              
    GRANT_OPTION                    0


    Records affected: 1

    WHO_AM_I                        TMP$C5248_USR1
    WHO_WAS_GRANTED                 TMP$C5248_USR1                                                                                                                                                                                                                                              
    PRIVILEGE_TYPE                  M     
    ROLE_NAME                       TEST_ROLE1                                                                                                                                                                                                                                                  
    ROLE_OWNER                      TMP$C5248_USR0                                                                                                                                                                                                                                              
    GRANTED_BY                      SYSDBA                                                                                                                                                                                                                                                      
    GRANT_OPTION                    2


    Records affected: 1

    WHO_AM_I                        TMP$C5248_USR0
    WHO_WAS_GRANTED                 TMP$C5248_USR3                                                                                                                                                                                                                                              
    PRIVILEGE_TYPE                  M     
    ROLE_NAME                       TEST_ROLE1                                                                                                                                                                                                                                                  
    ROLE_OWNER                      TMP$C5248_USR0                                                                                                                                                                                                                                              
    GRANTED_BY                      SYSDBA                                                                                                                                                                                                                                                      
    GRANT_OPTION                    0


    Records affected: 1
    Records affected: 0

    WHO_AM_I                        TMP$C5248_USR1
    WHO_WAS_GRANTED                 TMP$C5248_USR1                                                                                                                                                                                                                                              
    PRIVILEGE_TYPE                  M     
    ROLE_NAME                       TEST_ROLE1                                                                                                                                                                                                                                                  
    ROLE_OWNER                      TMP$C5248_USR0                                                                                                                                                                                                                                              
    GRANTED_BY                      SYSDBA                                                                                                                                                                                                                                                      
    GRANT_OPTION                    2

    WHO_AM_I                        TMP$C5248_USR1
    WHO_WAS_GRANTED                 TMP$C5248_USR3                                                                                                                                                                                                                                              
    PRIVILEGE_TYPE                  M     
    ROLE_NAME                       TEST_ROLE1                                                                                                                                                                                                                                                  
    ROLE_OWNER                      TMP$C5248_USR0                                                                                                                                                                                                                                              
    GRANTED_BY                      SYSDBA                                                                                                                                                                                                                                                      
    GRANT_OPTION                    0


    Records affected: 2

    WHO_AM_I                        TMP$C5248_USR1
    WHO_WAS_GRANTED                 TMP$C5248_USR1                                                                                                                                                                                                                                              
    PRIVILEGE_TYPE                  M     
    ROLE_NAME                       TEST_ROLE1                                                                                                                                                                                                                                                  
    ROLE_OWNER                      TMP$C5248_USR0                                                                                                                                                                                                                                              
    GRANTED_BY                      SYSDBA                                                                                                                                                                                                                                                      
    GRANT_OPTION                    2


    Records affected: 1

    COUNT                           1

    WHO_AM_I                        TMP$C5248_USR0
    WHO_WAS_GRANTED                 TMP$C5248_USR1                                                                                                                                                                                                                                              
    PRIVILEGE_TYPE                  M     
    ROLE_NAME                       TEST_ROLE1                                                                                                                                                                                                                                                  
    ROLE_OWNER                      TMP$C5248_USR0                                                                                                                                                                                                                                              
    GRANTED_BY                      SYSDBA                                                                                                                                                                                                                                                      
    GRANT_OPTION                    2

    WHO_AM_I                        TMP$C5248_USR0
    WHO_WAS_GRANTED                 TMP$C5248_USR3                                                                                                                                                                                                                                              
    PRIVILEGE_TYPE                  M     
    ROLE_NAME                       TEST_ROLE1                                                                                                                                                                                                                                                  
    ROLE_OWNER                      TMP$C5248_USR0                                                                                                                                                                                                                                              
    GRANTED_BY                      SYSDBA                                                                                                                                                                                                                                                      
    GRANT_OPTION                    0

    WHO_AM_I                        TMP$C5248_USR0
    WHO_WAS_GRANTED                 TMP$C5248_USR2                                                                                                                                                                                                                                              
    PRIVILEGE_TYPE                  M     
    ROLE_NAME                       TEST_ROLE1                                                                                                                                                                                                                                                  
    ROLE_OWNER                      TMP$C5248_USR0                                                                                                                                                                                                                                              
    GRANTED_BY                      TMP$C5248_USR1                                                                                                                                                                                                                                              
    GRANT_OPTION                    0


    Records affected: 3
    Records affected: 0
    Records affected: 0

    WHO_AM_I                        TMP$C5248_USR1
    WHO_WAS_GRANTED                 TMP$C5248_USR1                                                                                                                                                                                                                                              
    PRIVILEGE_TYPE                  M     
    ROLE_NAME                       TEST_ROLE1                                                                                                                                                                                                                                                  
    ROLE_OWNER                      TMP$C5248_USR0                                                                                                                                                                                                                                              
    GRANTED_BY                      SYSDBA                                                                                                                                                                                                                                                      
    GRANT_OPTION                    2

    WHO_AM_I                        TMP$C5248_USR1
    WHO_WAS_GRANTED                 TMP$C5248_USR3                                                                                                                                                                                                                                              
    PRIVILEGE_TYPE                  M     
    ROLE_NAME                       TEST_ROLE1                                                                                                                                                                                                                                                  
    ROLE_OWNER                      TMP$C5248_USR0                                                                                                                                                                                                                                              
    GRANTED_BY                      SYSDBA                                                                                                                                                                                                                                                      
    GRANT_OPTION                    0

    WHO_AM_I                        TMP$C5248_USR1
    WHO_WAS_GRANTED                 TMP$C5248_USR2                                                                                                                                                                                                                                              
    PRIVILEGE_TYPE                  M     
    ROLE_NAME                       TEST_ROLE1                                                                                                                                                                                                                                                  
    ROLE_OWNER                      TMP$C5248_USR0                                                                                                                                                                                                                                              
    GRANTED_BY                      TMP$C5248_USR1                                                                                                                                                                                                                                              
    GRANT_OPTION                    0

    Records affected: 3
    Records affected: 0
    Records affected: 0
  """
expected_stderr_2 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -REVOKE failed
    -TMP$C5248_USR1 is not grantor of ROLE on TEST_ROLE1 to TMP$C5248_USR1.

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -DROP ROLE TEST_ROLE1 failed
    -no permission for DROP access to ROLE TEST_ROLE1
  """

@pytest.mark.version('>=4.0')
def test_core_5248_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_expected_stderr == act_2.clean_stderr
    assert act_2.clean_expected_stdout == act_2.clean_stdout

