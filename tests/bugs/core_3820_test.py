#coding:utf-8
#
# id:           bugs.core_3820
# title:        RDB$TYPES contain duplicate character sets
# decription:   
# tracker_id:   CORE-3820
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
    select rdb$field_name, rdb$type_name, count(rdb$type_name)
    from rdb$types
    group by rdb$field_name, rdb$type_name
    having count(rdb$type_name) > 1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.execute()

