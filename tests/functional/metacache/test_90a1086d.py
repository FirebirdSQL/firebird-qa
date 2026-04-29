#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/90a1086d4803797c6135bc72eb4f9d129b054a2e
TITLE:       Fixed illegal error and assert raised when routine removed in same transaction where it was created
DESCRIPTION:
    CREATE standalone function/procerude and DROPPING it in same transaction caused fail with weird message
    "SQLSTATE = 42000 / unsuccessful metadata update / -Function NN not found".
NOTES:
    [29.04.2026] pzotov
    The bug has been found occasionally by analysis of fail reasons of some replicatiion-related tests.
    These tests invoke script $QA_HOME/files/drop-all-db-objects.sql which, in turn, had wrong WHERE-expression
    in queries that obtain data for standalone procedures and functions. See comments in this script for details.
    See also letters to Alex: 27.04.2026 17:15; 29.04.2026 14:00.
    Checked on 6.0.0.1923-0-90a1086
"""

import pytest
from firebird.qa import *

COMPLETED_MSG = 'Ok'
test_sql = f"""
    set bail OFF;
    set heading off;
    set autoddl off;
    set autoterm on;
    commit;
    create function fn_test returns int as begin return 1; end;
    drop function fn_test;
    commit;
    select '{COMPLETED_MSG}' as msg from rdb$database;
"""

db = db_factory()
act = isql_act('db', test_sql)

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = f"""
        {COMPLETED_MSG}
    """
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
