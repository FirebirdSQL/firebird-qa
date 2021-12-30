#coding:utf-8
#
# id:           bugs.gh_7062
# title:        Creation of expression index does not release its statement correctly
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/7062
#               
#                   Confirmed bug on 5.0.0.321.
#                   Checked on 5.0.0.336 - all fine.
#                   Checked on 4.0.1.2682 (11.12.2021) - all OK, reduced min_version to 4.0.1
#                
# tracker_id:   
# min_versions: ['4.0.1']
# versions:     4.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- case-1:
    create table test_1 (n integer);
    create table test_2 (n integer);
    create index test_1_expr on test_1 computed by ((select n from test_2));
    drop table test_1;
    commit;
    drop table test_2; -- this must NOT fail (raised "SQLSTATE = 42000 / object in use" before fix)

    -- case-2:
    create table test_a (n integer);
    create table test_b (n integer);
    insert into test_a values (0);
    commit;
    create index test_a_expr on test_a computed by (1 / 0 + (select 1 from test_b));
    drop table test_a;
    commit;
    drop table test_b; -- this must NOT fail (raised "SQLSTATE = 42000 / object in use" before fix)

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22012
    Expression evaluation error for index "***unknown***" on table "TEST_A"
    -arithmetic exception, numeric overflow, or string truncation
    -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.
"""

@pytest.mark.version('>=4.0.1')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
