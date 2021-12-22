#coding:utf-8
#
# id:           bugs.core_6440
# title:        Expression indexes containing COALESCE inside cannot be matched by the optimizer after migration from v2.5 to v3.0
# decription:   
#                   Confirmed bug on 3.0.7.33388 (wrong plans of queris specified in the ticked; need to RESTORE database from 2.5 on 3.x).
#                   Test uses .fbk that was created on FB 2.5.9, file: core6440-ods11.fbk
#               
#                   Checked on 4.0.0.2269; 3.0.8.33390 -- all OK.
#                 
# tracker_id:   CORE-6440
# min_versions: []
# versions:     3.0.8
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core6440-ods11.fbk', init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (TEST INDEX (PK_TEST))

    PLAN (TEST INDEX (TEST_IDX4))

    PLAN (TEST INDEX (TEST_IDX3))

    PLAN (TEST INDEX (TEST_IDX2))

    PLAN (TEST INDEX (TEST_IDX1))
"""

@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

