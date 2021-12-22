#coding:utf-8
#
# id:           bugs.core_4898
# title:        Speed up function creation and loading when there are many functions in the database
# decription:   
# tracker_id:   CORE-4898
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- See: http://sourceforge.net/p/firebird/code/62075
    set list on;
    select ri.rdb$relation_name,rs.rdb$field_name,rs.rdb$field_position 
    from rdb$indices ri join rdb$index_segments rs 
    using (rdb$index_name) 
    where ri.rdb$relation_name='RDB$FUNCTIONS' and rdb$field_name='RDB$FUNCTION_ID'; 
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$RELATION_NAME               RDB$FUNCTIONS
    RDB$FIELD_NAME                  RDB$FUNCTION_ID
    RDB$FIELD_POSITION              0
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

