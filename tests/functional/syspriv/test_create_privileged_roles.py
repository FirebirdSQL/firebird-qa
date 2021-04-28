#coding:utf-8
#
# id:           functional.syspriv.create_privileged_roles
# title:        Check ability of non-sysdba user to CREATE privileged role (but NOT use it)
# decription:   
#                  Checked on WI-T4.0.0.267.
#                
# tracker_id:   
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set wng off;
    set bail on;
    set list on;


    create or alter user u01 password '123' revoke admin role;
    revoke all on all from u01;
    grant create role to u01;
    commit;

    set term ^;
    execute block as
    begin
      begin
        execute statement 'drop role role_for_CREATE_PRIVILEGED_ROLES';
        when any do begin end
      end
      begin
        execute statement 'drop role role_for_USE_GRANTED_BY_CLAUSE';
        when any do begin end
      end
    end^
    set term ;^
    commit;

    create role role_for_CREATE_PRIVILEGED_ROLES set system privileges to CREATE_PRIVILEGED_ROLES;
    commit;
    grant default role_for_CREATE_PRIVILEGED_ROLES to user u01;
    commit;

    connect '$(DSN)' user u01 password '123';

    -- Here we check that U01 can CREATE privileged role but this is the ONLY what he can do,
    -- i.e. he is NOT granted with this role!
    create role role_for_USE_GRANTED_BY_CLAUSE SET SYSTEM PRIVILEGES TO USE_GRANTED_BY_CLAUSE;
    commit;

    select current_user as who_am_i,r.rdb$role_name,rdb$role_in_use(r.rdb$role_name),r.rdb$system_privileges
    from mon$database m cross join rdb$roles r;
    
    commit;

    connect '$(DSN)' user sysdba password 'masterkey';
    drop user u01;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
     WHO_AM_I                        U01
     RDB$ROLE_NAME                   RDB$ADMIN
     RDB$ROLE_IN_USE                 <false>
     RDB$SYSTEM_PRIVILEGES           FFFFFFFFFFFFFFFF

     WHO_AM_I                        U01
     RDB$ROLE_NAME                   ROLE_FOR_CREATE_PRIVILEGED_ROLES
     RDB$ROLE_IN_USE                 <true>
     RDB$SYSTEM_PRIVILEGES           0000800000000000

     WHO_AM_I                        U01
     RDB$ROLE_NAME                   ROLE_FOR_USE_GRANTED_BY_CLAUSE
     RDB$ROLE_IN_USE                 <false>
     RDB$SYSTEM_PRIVILEGES           0000100000000000
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

