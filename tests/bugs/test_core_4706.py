#coding:utf-8
#
# id:           bugs.core_4706
# title:        ISQL pads blob columns wrongly when the column alias has more than 17 characters
# decription:   
# tracker_id:   CORE-4706
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set blob all;
    select cast('a' as blob) a, 1, cast('a' as blob) x2345678901234567890, 2 from rdb$database; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                A     CONSTANT X2345678901234567890     CONSTANT 
              0:2            1                  0:1            2 
A:  
a
X2345678901234567890:  
a
  """

@pytest.mark.version('>=3.0')
def test_core_4706_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

