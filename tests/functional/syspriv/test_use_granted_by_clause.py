#coding:utf-8
#
# id:           functional.syspriv.use_granted_by_clause
# title:        Check ability to query, modify and deleting data plus add/drop constraints on any table.
# decription:   
#                  Two users are created, U01 and U02. 
#                  User U01 is granted with system privilege USE_GRANTED_BY_CLAUSE.
#                  User U02 has NO any privilege.
#                  User U01 then creates table and issue GRANT SELECT statement for U02 as it was granted by SYSDBA.
#                  Then we 
#                  1) check result (contrent of RDB$ tables) 
#                  2) connect as U02 and query this table - this should work OK
#                  3) connect as U01 and revoke grant on just queried table from U02
#                  4) connect again as U02 and repeat select - this shoiuld fail.
#               
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
    create or alter user u02 password '456' revoke admin role;
    revoke all on all from u01;
    revoke all on all from u02;
    grant create table to u01;
    commit;

    set term ^;
    execute block as
    begin
      execute statement 'drop role role_for_use_granted_by_clause';
      when any do begin end
    end^
    set term ;^
    commit;

    -- Add/change/delete non-system records in RDB$TYPES
    create role role_for_use_granted_by_clause set system privileges to USE_GRANTED_BY_CLAUSE;
    commit;
    grant default role_for_use_granted_by_clause to user u01;
    commit;

    connect '$(DSN)' user u01 password '123';
    select current_user as who_am_i,r.rdb$role_name,rdb$role_in_use(r.rdb$role_name),r.rdb$system_privileges
    from mon$database m cross join rdb$roles r;
    commit;

    recreate table test_u01(id int, who_is_author varchar(31) default current_user);
    commit;
    insert into test_u01(id) values(1);
    commit;

    grant select on table test_u01 to u02 granted by sysdba;
    commit;

    -- this should give output with rdb$grantor = 'SYSDBA' despite that actual grantor was 'U01':
    select * from rdb$user_privileges where rdb$relation_name=upper('test_u01') and rdb$user=upper('u02');
    commit;

    connect '$(DSN)' user u02 password '456';
    select current_user as who_am_i, u.* from test_u01 u;
    commit;

    connect '$(DSN)' user u01 password '123';
    revoke select on test_u01 from u02 granted by sysdba;
    commit;

    set bail off;
    connect '$(DSN)' user u02 password '456';
    select current_user as who_am_i, u.* from test_u01 u; -- this should FAIL
    commit;
    set bail on;

    connect '$(DSN)' user sysdba password 'masterkey';
    drop user u01;
    drop user u02;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WHO_AM_I                        U01
    RDB$ROLE_NAME                   RDB$ADMIN
    RDB$ROLE_IN_USE                 <false>
    RDB$SYSTEM_PRIVILEGES           FFFFFFFFFFFFFFFF

    WHO_AM_I                        U01
    RDB$ROLE_NAME                   ROLE_FOR_USE_GRANTED_BY_CLAUSE
    RDB$ROLE_IN_USE                 <true>
    RDB$SYSTEM_PRIVILEGES           0000100000000000

    RDB$USER                        U02
    RDB$GRANTOR                     SYSDBA
    RDB$PRIVILEGE                   S
    RDB$GRANT_OPTION                0
    RDB$RELATION_NAME               TEST_U01
    RDB$FIELD_NAME                  <null>
    RDB$USER_TYPE                   8
    RDB$OBJECT_TYPE                 0
    
    WHO_AM_I                        U02
    ID                              1
    WHO_IS_AUTHOR                   U01
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    no permission for SELECT access to TABLE TEST_U01
    -Effective user is U02
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

