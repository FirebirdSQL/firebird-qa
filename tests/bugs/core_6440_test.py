#coding:utf-8

"""
ID:          issue-6674
ISSUE:       6674
TITLE:       Expression indexes containing COALESCE inside cannot be matched by the optimizer after migration from v2.5 to v3.0
DESCRIPTION:
  Test uses .fbk that was created on FB 2.5.9, file: core6440-ods11.fbk
JIRA:        CORE-6440
"""

import pytest
from firebird.qa import *

db = db_factory(from_backup='core6440-ods11.fbk')

test_script = """
    set planonly;
    --set echo on;

    --Uses a proper index: PLAN (TEST INDEX (PK_TEST))
    select * from test where field_1 = 1;



    --Uses a proper index: PLAN (TEST INDEX (TEST_IDX4))
    select * from test where (UPPER(FIELD_2)) = 'TEST1';



    --Doesn't uses a proper index: PLAN (TEST NATURAL)
    select * from test where (UPPER(COALESCE(FIELD_2,''))) = 'TEST1';



    --Uses PLAN (TEST INDEX (TEST_IDX2))
    select * from test where (UPPER(FIELD_2)||UPPER(FIELD_3)) = 'TEST1TEST1_1';



    --Doesn't uses a proper index: PLAN (TEST NATURAL)
    select * from test where (UPPER(COALESCE(FIELD_2,''))||UPPER(COALESCE(FIELD_3,''))) = 'TEST1TEST1_1';

"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (TEST INDEX (PK_TEST))

    PLAN (TEST INDEX (TEST_IDX4))

    PLAN (TEST INDEX (TEST_IDX3))

    PLAN (TEST INDEX (TEST_IDX2))

    PLAN (TEST INDEX (TEST_IDX1))
"""

@pytest.mark.version('>=3.0.8')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
