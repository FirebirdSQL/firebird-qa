#coding:utf-8

"""
ID:          issue-5041
ISSUE:       5041
TITLE:       Expression 'where bool_field IS true | false' should also use index as 'where bool_field = true | false' (if such index exists)
DESCRIPTION:
NOTES:
[28.01.2019]
  Changed expected PLAN of execution after dimitr's letter 28.01.2019 17:28:
  'is NOT <bool>' and 'is distinct from <bool>' should use  PLAN NATURAL.
JIRA:        CORE-4735
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test(x boolean, unique(x) using index test_x);
    commit;

    set plan on;
    select 1 from test where x = true ;
    select 1 from test where x is true ;
    select 0 from test where x = false ;
    select 0 from test where x is false ;
    select 1 from test where x is not true ; -- this must have plan NATURAL, 26.01.2019
    select 1 from test where x is distinct from true ; -- this must have plan NATURAL, 26.01.2019
    select 1 from test where x is not false ; -- this must have plan NATURAL, 26.01.2019
    select 1 from test where x is distinct from false ; -- this must have plan NATURAL, 26.01.2019
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (TEST INDEX (TEST_X))
    PLAN (TEST INDEX (TEST_X))
    PLAN (TEST INDEX (TEST_X))
    PLAN (TEST INDEX (TEST_X))
    PLAN (TEST NATURAL)
    PLAN (TEST NATURAL)
    PLAN (TEST NATURAL)
    PLAN (TEST NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

