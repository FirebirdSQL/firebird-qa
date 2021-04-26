#coding:utf-8
#
# id:           bugs.core_5060
# title:        Cannot CREATE VIEW that selects from a system table, despite having all grants
# decription:   : 
#                  Confirmed fail on WI-V3.0.0.32253: got
#                   create or alter view v_tmp$5060_u1 as select 1 i from rdb$database;
#                   Statement failed, SQLSTATE = 28000
#                   unsuccessful metadata update
#                   -CREATE OR ALTER VIEW V_JOHN1 failed
#                   -no permission for SELECT access to TABLE/VIEW RDB$DATABASE
#                 Checked on WI-V3.0.0.32272 (SS/SC/CS).
#                
# tracker_id:   CORE-5060
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bail on;
    set wng off;
    set count on;
    set list on;

    create or alter user tmp$5060_u1 password '123' revoke admin role;
    create or alter user tmp$5060_u2 password '456' revoke admin role;

    revoke all on all from tmp$5060_u1;
    revoke all on all from tmp$5060_u2;
    commit;

    set term ^;
    execute block as
    begin
      execute statement 'drop role dba_assistant';
      when any do begin end
    end
    ^
    set term ;^
    commit;

    create role dba_assistant;
    commit;

    grant create view to user tmp$5060_u1;
    grant alter any view to user tmp$5060_u1;
    grant drop any view  to user tmp$5060_u1;

    grant create view to role dba_assistant;
    grant alter any view to role dba_assistant;
    grant drop any view  to role dba_assistant;
    grant dba_assistant to tmp$5060_u2;
    commit;

    connect '$(DSN)' user tmp$5060_u1 password '123';

    create or alter view v_tmp$5060_u1 as select 1 i from rdb$database;
    create or alter view v_tmp$5060_u2 as select v.i as u1, r.i as u2 from v_tmp$5060_u1 v join (select 1 i from rdb$database) r using (i);

    select current_user, current_role, v.* from v_tmp$5060_u1 v;
    select current_user, current_role, v.* from v_tmp$5060_u2 v;

    commit;

    connect '$(DSN)' user tmp$5060_u2 password '456' role 'DBA_ASSISTANT';

    create or alter view v_tmp$5060_r1 as select 1 i from rdb$database;
    create or alter view v_tmp$5060_r2 as select v.i as r1, r.i as r2 from v_tmp$5060_r1 v join (select 1 i from rdb$database) r using (i);

    select current_user, current_role, v.* from v_tmp$5060_r1 v;
    select current_user, current_role, v.* from v_tmp$5060_r2 v;

    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    drop user tmp$5060_u1;
    drop user tmp$5060_u2;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    USER                            TMP$5060_U1
    ROLE                            NONE
    I                               1
    Records affected: 1
    USER                            TMP$5060_U1
    ROLE                            NONE
    U1                              1
    U2                              1
    Records affected: 1
    USER                            TMP$5060_U2
    ROLE                            DBA_ASSISTANT
    I                               1
    Records affected: 1
    USER                            TMP$5060_U2
    ROLE                            DBA_ASSISTANT
    R1                              1
    R2                              1
    Records affected: 1    
  """

@pytest.mark.version('>=3.0')
def test_core_5060_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

