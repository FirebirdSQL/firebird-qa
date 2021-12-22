#coding:utf-8
#
# id:           bugs.core_0507
# title:        ambiguous statements return unpredictable results
# decription:   
#                
# tracker_id:   CORE-507
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;
    select r.rdb$relation_name, rc.rdb$relation_name, rc.rdb$constraint_type
    from rdb$relations r left join rdb$relation_constraints rc
    on r.rdb$relation_name = rc.rdb$relation_name
    order by rdb$relation_name;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42702
    Dynamic SQL Error
    -SQL error code = -204
    -Ambiguous field name between a field and a field in the select list with name
    -RDB$RELATION_NAME
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

