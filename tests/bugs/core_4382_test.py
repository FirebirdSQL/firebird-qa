#coding:utf-8

"""
ID:          issue-4704
ISSUE:       4704
TITLE:       User savepoints are not released on commit
DESCRIPTION:
  Added separate code for 4.0: one need to be sure that all changes have been flushed on disk before we launch gstat.
  See letter from hvlad, 02.02.2019 22:30.
  ::: NOTE :::
  !! It looks strange but if we put preparing statement in 'init_script' section than result of 'gstat -i' will be WRONG,
  even if we do db_conn.close() before runProgram('gstat' ...) !!
JIRA:        CORE-4382
FBTEST:      bugs.core_4382
"""

import pytest
from firebird.qa import *

substitutions = [('^((?!nodes).)*$', ''), ('Root page: [0-9]+,', ''), ('Depth', 'depth')]

init_script = """
    create table g_test (f integer);
    create index g_ind on g_test (f);
    insert into g_test values (1);
    commit;
    update g_test set f=2;
    savepoint a;
    update g_test set f=3;
    savepoint b;
    update g_test set f=4;
    savepoint c;
    update g_test set f=5;
    savepoint d;
    update g_test set f=6;
    savepoint e;
    update g_test set f=7;
    commit;
    select * from g_test;
    COMMIT;
    -- Confirmed result of "gstat -i"
    -- 1) for 3.0 Alpha1 & Alpha2:
    -- Root page: 203, depth: 1, leaf buckets: 1, nodes: 6
    --                                                   ^- orphans, must be: 1
    -- 2) for 2.5.3:
    -- Depth: 1, leaf buckets: 1, nodes: 6
    -- ^- upper case!                    ^- orphans, must be: 1
"""

# version: 3.0

db_1 = db_factory(init=init_script)

act_1 = python_act('db_1', substitutions=substitutions)

expected_stdout_1 = """
    Root page: 203, depth: 1, leaf buckets: 1, nodes: 1
"""

@pytest.mark.version('>=3,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.gstat(switches=['-i'])
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0

db_2 = db_factory()

act_2 = python_act('db_2', substitutions=substitutions)

expected_stdout_2 = """
    Root page: 203, depth: 1, leaf buckets: 1, nodes: 1
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.isql(switches=['-q'], input=init_script)
    act_2.reset()
    act_2.expected_stdout = expected_stdout_2
    act_2.gstat(switches=['-i'])
    assert act_2.clean_stdout == act_2.clean_expected_stdout



