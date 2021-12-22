#coding:utf-8
#
# id:           bugs.core_1869
# title:        Roles granting/revoking logic
# decription:   
#                  Test for "grant ... to ... GRANTED BY ..." clause
#                  Checked on:
#                       2.5.9.27107: OK, 0.656s.
#                       3.0.4.32924: OK, 4.313s.
#                       4.0.0.916: OK, 2.406s.
#                
# tracker_id:   CORE-1869
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create user tmp$c1869_u01 password '123';
    create user tmp$c1869_u02 password '123';
    set term ^;
    execute block as
    begin
      execute statement 'drop role boss';
      when any do begin end
    end
    ^
    set term ;^
    commit;
    create role boss;
    commit;

    recreate view v_grants as
    select
         p.rdb$user                      as who_was_granted
        ,p.rdb$privilege                 as privilege_type 
        ,p.rdb$relation_name             as role_name       
        ,r.rdb$owner_name                as role_owner
        ,p.rdb$grantor                   as granted_by
        ,p.rdb$grant_option              as grant_option   
    from rdb$user_privileges p
    left join rdb$roles r on p.rdb$relation_name = r.rdb$role_name
    where 
        p.rdb$object_type=13
        and upper(p.rdb$user) != upper('SYSDBA') -- we have to add this because role RDB$ADMIN is shown as granted to SYSDBA in 4.0.x
    ;
    commit;
    grant select on v_grants to public;
    commit;

    set list on;

    grant boss to tmp$c1869_u01;
    grant boss to tmp$c1869_u02 granted by tmp$c1869_u01;
    commit;

    -- TWO record should be printed:
    select 'init' as msg, v.* from v_grants v;
    commit;

    connect '$(DSN)' user 'tmp$c1869_u02' password '123' role 'BOSS';

    select current_user, current_role from rdb$database;
    commit;

    connect '$(DSN)' user 'tmp$c1869_u01' password '123';

    -- this should PASS without error: user "_u01" was specified as GRANTOR in the statement: 
    -- "grant boss to ..._u02 granted by ..._u01" (see above):
    revoke boss from tmp$c1869_u02; 
    commit;

    connect '$(DSN)' user 'tmp$c1869_u02' password '123' role 'BOSS';

    -- Now user ..._u02 should be connected WITHOUT any actual role:
    select current_user, current_role from rdb$database;

    -- now only ONE record should be printed:
    select 'fini' as msg, v.* from v_grants v;
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    drop user tmp$c1869_u01;
    drop user tmp$c1869_u02;
    commit;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             init
    WHO_WAS_GRANTED                 TMP$C1869_U01
    PRIVILEGE_TYPE                  M
    ROLE_NAME                       BOSS
    ROLE_OWNER                      SYSDBA
    GRANTED_BY                      SYSDBA
    GRANT_OPTION                    0

    MSG                             init
    WHO_WAS_GRANTED                 TMP$C1869_U02
    PRIVILEGE_TYPE                  M
    ROLE_NAME                       BOSS
    ROLE_OWNER                      SYSDBA
    GRANTED_BY                      TMP$C1869_U01
    GRANT_OPTION                    0

    USER                            TMP$C1869_U02
    ROLE                            BOSS

    USER                            TMP$C1869_U02
    ROLE                            NONE

    MSG                             fini
    WHO_WAS_GRANTED                 TMP$C1869_U01
    PRIVILEGE_TYPE                  M
    ROLE_NAME                       BOSS
    ROLE_OWNER                      SYSDBA
    GRANTED_BY                      SYSDBA
    GRANT_OPTION                    0
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

