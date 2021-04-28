#coding:utf-8
#
# id:           bugs.core_1677
# title:        Floor & ceiling functions give wrong results with exact numeric arguments
# decription:   Floor & ceiling functions give wrong results with exact numeric arguments
#               select floor(cast(1500 as numeric(18,5))) from rdb$database -> -4827 (wrong)
#               select floor(cast(1500 as numeric(18,4))) from rdb$database -> 1500 (correct)
#               select ceiling(cast(1500 as numeric(18,5))) from rdb$database -> -4826 (wrong)
#               
#               Actually, any precision higher than 6 gives a wrong result.
# tracker_id:   CORE-1677
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1677

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select floor(cast(1500 as numeric(18,5))) F1,floor(cast(1500 as numeric(18,4))) F2, ceiling(cast(1500 as numeric(18,5))) F3 from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                   F1                    F2                    F3
===================== ===================== =====================
                 1500                  1500                  1500

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

