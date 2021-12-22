#coding:utf-8
#
# id:           bugs.core_0335
# title:        Unsuccessful execution caused by system error <...> bad BLR -- invalid stream
# decription:   
#                  Original ticket title: "Lost connexion with Big request"
#                  Test checks that:
#                  1) we *can* run query with <N> unions, where <N> is limit specific for 2.5.x vs 3.x
#                  2) we can *not* run query with <N+1> unions.
#                  Actual value of <N> is 128 for 2.5.x (NOT 255 as errormessage issues!) and 255 for 3.0.
#               
#                  Checked on WI-V2.5.7.27025, WI-V3.0.1.32598.
#                
# tracker_id:   CORE-335
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test(id int);
    commit;
    insert into test select 1 from rdb$types rows 10;
    commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set count on;
    
    -- ##########################
    -- FIRST  QUERY: SHOULD PASS.
    -- ##########################
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 10
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 20
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 30
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 40
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 50
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 60
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 70
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 80
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 90
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --100

    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --110
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --120
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- last allowed in 2.5.7; add subsequent leads in 2.5.x to Too many Contexts of Relation/Procedure/Views. Maximum allowed is 255
    select first 5 * from test union 
    select first 5 * from test union --130
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --140
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --150
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --160
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --170
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --180
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --190
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --200

    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --210
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --220
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --230
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --240
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --250
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test ------------------- last allowed in 3.0
    ; /* union select first 5 * from test; */


    -- ##########################
    -- SECOND QUERY: SHOULD FAIL.
    -- ##########################
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 10
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 20
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 30
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 40
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 50
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 60
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 70
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 80
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- 90
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --100

    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --110
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --120
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union -- last allowed in 2.5.7; add subsequent leads in 2.5.x to Too many Contexts of Relation/Procedure/Views. Maximum allowed is 255
    select first 5 * from test union 
    select first 5 * from test union --130
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --140
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --150
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --160
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --170
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --180
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --190
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --200

    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --210
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --220
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --230
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --240
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union --250
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test union
    select first 5 * from test ------------------- last allowed in 3.0
    union all select first 5 * from test;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    Records affected: 1
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 54001
    Dynamic SQL Error
    -Too many Contexts of Relation/Procedure/Views. Maximum allowed is 256
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

