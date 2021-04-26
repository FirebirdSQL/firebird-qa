#coding:utf-8
#
# id:           bugs.core_4477
# title:        Field RDB$MAP_TO_TYPE is not present in RDB$TYPES
# decription:   
# tracker_id:   CORE-4477
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select rdb$field_name,rdb$type,rdb$type_name,rdb$system_flag from rdb$types where upper(rdb$field_name) = upper('rdb$map_to_type') order by rdb$type;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
   RDB$FIELD_NAME                  RDB$MAP_TO_TYPE                                                                              
   RDB$TYPE                        0
   RDB$TYPE_NAME                   USER                                                                                         
   RDB$SYSTEM_FLAG                 1

   RDB$FIELD_NAME                  RDB$MAP_TO_TYPE                                                                              
   RDB$TYPE                        1
   RDB$TYPE_NAME                   ROLE                                                                                         
   RDB$SYSTEM_FLAG                 1
  """

@pytest.mark.version('>=3.0')
def test_core_4477_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

