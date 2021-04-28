#coding:utf-8
#
# id:           bugs.core_3420
# title:        BOOLEAN not present in system table RDB$TYPES
# decription:   
# tracker_id:   CORE-3420
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
    set list on;
    select
        rdb$field_name,
        rdb$type,
        rdb$type_name,
        rdb$system_flag
    from rdb$types t
    where upper(t.rdb$type_name) = upper('boolean')
    order by t.rdb$field_name;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$FIELD_NAME                  RDB$FIELD_TYPE
    RDB$TYPE                        23
    RDB$TYPE_NAME                   BOOLEAN
    RDB$SYSTEM_FLAG                 1
    RDB$FIELD_NAME                  RDB$FUNCTION_TYPE
    RDB$TYPE                        1
    RDB$TYPE_NAME                   BOOLEAN
    RDB$SYSTEM_FLAG                 1
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

