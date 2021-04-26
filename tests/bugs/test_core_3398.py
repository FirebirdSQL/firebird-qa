#coding:utf-8
#
# id:           bugs.core_3398
# title:        GRANT ADMIN ROLE not accepted
# decription:   
# tracker_id:   CORE-3398
# min_versions: ['2.5.0']
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
    -- See ticket issue: Alexander Peshkov added a comment - 21/Mar/11 03:10 PM
    -- Does not require frontporting - FB3 is using another way to access security database 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_core_3398_1(act_1: Action):
    act_1.execute()

