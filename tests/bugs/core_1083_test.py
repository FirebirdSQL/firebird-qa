#coding:utf-8

"""
ID:          issue-1504
ISSUE:       1504
TITLE:       User (not SYSDBA) what have privileges with grant option, can't revoke privileges, granted by other user or SYSDBA
DESCRIPTION:
JIRA:        CORE-1083
FBTEST:      bugs.core_1083
"""

import pytest
from firebird.qa import *

substitutions = [('set echo .*', ''),
                   ('-TMP\\$C1083 is not grantor of (UPDATE|Update|update) on TAB2 to ROLE1.',
                    '-TMP$C1083 is not grantor of UPDATE on TAB2 to ROLE1.')]

db = db_factory()

test_script = """
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

    connect 'localhost:$(DATABASE_LOCATION)test.fdb' user 'TMP$C1083' password 'QweRtyUioP';
    --set bail on;
    set echo on;
    grant update(col1) on tab1 to role1;
    revoke update(col1) on tab1 from role1;
    revoke update(col2) on tab2 from role1;
    set echo off;
    commit;

    connect 'localhost:$(DATABASE_LOCATION)test.fdb' user 'SYSDBA' password 'masterkey';
    set echo on;
    drop user tmp$c1083;
    set echo off;
    commit;
    --  ('-TMP\\$C1083 is not grantor.*', '')
"""

act = isql_act('db', test_script, substitutions=substitutions)

expected_stdout = """
    grant update(col1) on tab1 to role1;
    revoke update(col1) on tab1 from role1;
    revoke update(col2) on tab2 from role1;
    drop user tmp$c1083;
"""

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -REVOKE failed
    -TMP$C1083 is not grantor of UPDATE on TAB2 to ROLE1.
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

