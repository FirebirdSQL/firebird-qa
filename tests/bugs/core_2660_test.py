#coding:utf-8
#
# id:           bugs.core_2660
# title:        COUNT(*) incorrectly returns 0 when a condition of an outer join doesn't match
# decription:   
# tracker_id:   CORE-2660
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """select b.*
  from rdb$database a
  left join (
    select count(*) c
      from rdb$database
  ) b on 1 = 0;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                    C
=====================
               <null>

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

