#coding:utf-8
#
# id:           bugs.core_1362
# title:        Too large numbers cause positive infinity to be inserted into database
# decription:   
# tracker_id:   CORE-1362
# min_versions: []
# versions:     2.5.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test (col1 double precision);
    commit;
    -- this should PASS:
    insert into test values( 1.79769313486231570E+308 );
    -- this is too big, should raise exception:
    insert into test values( 1.79769313486232e+308 );
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22003
    arithmetic exception, numeric overflow, or string truncation
    -numeric value is out of range
"""

@pytest.mark.version('>=2.5.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    recreate table test (col1 double precision);
    commit;
    -- this should PASS:
    insert into test values( 1.79769313486231570E+308 );
    -- this is too big, should raise exception:
    insert into test values( 1.79769313486232e+308 );
    commit;
"""

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stderr_2 = """
    Statement failed, SQLSTATE = 22003
    Floating-point overflow.  The exponent of a floating-point operation is greater than the magnitude allowed.
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_stderr == act_2.clean_expected_stderr

