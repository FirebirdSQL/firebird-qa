#coding:utf-8
#
# id:           bugs.core_6345
# title:        Server crashes on overflow of division result
# decription:   
#                   Confirmed bug on 4.0.0.2076, 3.0.6.33322
#                   Checked on 4.0.0.2078, 3.0.6.33326 - all OK.
#                   (intermediate snapshots with timestamps: 26.06.20 06:36, 07:26)
#               
#                   27.07.2021: separated code for FB 4.x+ because of fix #6874
#                   ("Literal 65536 (interpreted as int) can not be multiplied by itself w/o cast if result more than 2^63-1"):
#                   no more error with SQLSTATE = 22003 after this fix.
#                   Checked on 5.0.0.113, 4.0.1.2539.
#                
# tracker_id:   CORE-6345
# min_versions: ['3.0.6']
# versions:     3.0.6, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    select -922337203685477.5808/-1.0 from rdb$database; 
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22003
    Integer overflow.  The result of an integer operation caused the most significant bit of the result to carry.
"""

@pytest.mark.version('>=3.0.6,<4.0')
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
    set heading off;
    select -922337203685477.5808/-1.0 from rdb$database; 
"""

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    922337203685477.58080
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout

