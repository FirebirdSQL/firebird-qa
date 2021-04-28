#coding:utf-8
#
# id:           bugs.core_1083
# title:        User (not SYSDBA) what have privileges with grant option, can't revoke privileges, granted by other user or SYSDBA
# decription:   
# tracker_id:   CORE-1083
# min_versions: ['2.1.0']
# versions:     3.0
# qmid:         bugs.core_1083

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('set echo .*', ''), ('-TMP\\$C1083 is not grantor of (UPDATE|Update|update) on TAB2 to ROLE1.', '-TMP$C1083 is not grantor of UPDATE on TAB2 to ROLE1.')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Refactored 05-JAN-2016: removed dependency on recource 'test_user'.
    -- Checked on WI-V3.0.0.32266 (SS/SC/CS).
    -- Checked 06.08.2018: added 'substitutions' because different case if some words in error message
    -- ('Update' in 3.0.x vs 'UPDATE' in 4.0)
    -- 3.0.4.33021: OK, 1.563s.
    -- 4.0.0.1143: OK, 2.703s.

    create or alter user tmp$c1083 password 'QweRtyUioP';
    commit;
    recreate table tab1(col1 integer);
    recreate table tab2(col2 integer);
    commit;
    create role role1;
    grant update (col1) on tab1 to tmp$c1083 with grant option;
    grant update (col2) on tab2 to role1;
    commit;
    
    connect 'localhost:$(DATABASE_LOCATION)bugs.core_1083.fdb' user 'TMP$C1083' password 'QweRtyUioP';
    --set bail on;
    set echo on;
    grant update(col1) on tab1 to role1;
    revoke update(col1) on tab1 from role1;
    revoke update(col2) on tab2 from role1;
    set echo off;
    commit;
    
    connect 'localhost:$(DATABASE_LOCATION)bugs.core_1083.fdb' user 'SYSDBA' password 'masterkey';
    set echo on;
    drop user tmp$c1083;
    set echo off;
    commit;
    --  ('-TMP\\$C1083 is not grantor.*', '')
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    grant update(col1) on tab1 to role1;
    revoke update(col1) on tab1 from role1;
    revoke update(col2) on tab2 from role1;
    drop user tmp$c1083;
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -REVOKE failed
    -TMP$C1083 is not grantor of UPDATE on TAB2 to ROLE1.
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

