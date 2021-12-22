#coding:utf-8
#
# id:           bugs.core_5612
# title:        Gradual slowdown compilation (create, recreate or drop) of views
# decription:   
#                   Checked on 4.0.0.1479: OK, 1.336s.
#                
# tracker_id:   CORE-5612
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set count on;
    select ri.rdb$index_id idx_id,rs.rdb$field_position pos, rs.rdb$field_name key
    from rdb$indices ri
    left join rdb$index_segments rs on ri.rdb$index_name = rs.rdb$index_name
    where ri.rdb$relation_name = upper('rdb$dependencies')
    order by 1,2;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    IDX_ID                          1
    POS                             0
    KEY                             RDB$DEPENDENT_NAME
    IDX_ID                          1
    POS                             1
    KEY                             RDB$DEPENDENT_TYPE
    IDX_ID                          2
    POS                             0
    KEY                             RDB$DEPENDED_ON_NAME

    IDX_ID                          2
    POS                             1
    KEY                             RDB$DEPENDED_ON_TYPE
    IDX_ID                          2
    POS                             2
    KEY                             RDB$FIELD_NAME

    Records affected: 5
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

