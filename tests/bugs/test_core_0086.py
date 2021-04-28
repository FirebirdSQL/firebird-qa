#coding:utf-8
#
# id:           bugs.core_0086
# title:        Index bug
# decription:   Can not fetch the data when Index is use
# tracker_id:   CORE-86
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_86

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core86.fbk', init=init_script_1)

test_script_1 = """Select * from YLK A where PH = '0021'
and HPBH = '492'
and CD = 'MG'
and JLDW = 'JIAN'
and JZDW = 'DUN'
and CK = '8K'
and HW = '1.8'
and SH='1.81';"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """ID_YLK PH                           HPBH CD                   JLDW   JZDW   CK               HW                              SH
============ ==================== ============ ==================== ====== ====== ================ ============ =====================
         110 0021                          492 MG                   JIAN   DUN    8K               1.8                        1.81000

"""

@pytest.mark.version('>=2.1')
def test_core_0086_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

