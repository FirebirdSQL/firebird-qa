#coding:utf-8
#
# id:           bugs.core_4460
# title:        Expressions containing some built-in functions may be badly optimized
# decription:   
# tracker_id:   CORE-4460
# min_versions: ['2.5.3']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('RDB\\$INDEX_[0-9]+', 'RDB\\$INDEX_')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;
    select * from (
       select rdb$relation_name from rdb$relations
       union
       select rdb$field_name from rdb$fields
    ) as dt (name) where dt.name=''
    ;
    select * from (
      select rdb$relation_name from rdb$relations
      union
      select rdb$field_name from rdb$fields
    ) as dt (name) where dt.name = left('', 0)
    ;
    
    select * from (
      select rdb$relation_name from rdb$relations
      union
      select rdb$field_name from rdb$fields
    ) as dt (name) where dt.name = minvalue('', '')
    ;
    
    select * from (
      select rdb$relation_name from rdb$relations
      union
      select rdb$field_name from rdb$fields
    ) as dt (name) where dt.name = rpad('', 0, '')
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN SORT (DT RDB$RELATIONS INDEX (RDB$INDEX_0), DT RDB$FIELDS INDEX (RDB$INDEX_2))
    PLAN SORT (DT RDB$RELATIONS INDEX (RDB$INDEX_0), DT RDB$FIELDS INDEX (RDB$INDEX_2))
    PLAN SORT (DT RDB$RELATIONS INDEX (RDB$INDEX_0), DT RDB$FIELDS INDEX (RDB$INDEX_2))
    PLAN SORT (DT RDB$RELATIONS INDEX (RDB$INDEX_0), DT RDB$FIELDS INDEX (RDB$INDEX_2))
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

