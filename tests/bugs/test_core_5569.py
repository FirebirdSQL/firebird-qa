#coding:utf-8
#
# id:           bugs.core_5569
# title:        ISQL incorrectly pads UNICODE_FSS/UTF8 columns when they use a collation
# decription:   
#                   30SS, build 3.0.3.32738: OK, 0.766s.
#                   40SS, build 4.0.0.680: OK, 0.859s.
#                
# tracker_id:   CORE-5569
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list OFF; -- for this test we have to check table-wise view rather than list
    select 
        _utf8 '1234567890' collate unicode as f_with_collate, 
        _utf8 '1234567890' as f_without_collate,
        '|' as d
    from rdb$database;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    F_WITH_COLLATE F_WITHOUT_COLLATE D
    ============== ================= ======
    1234567890     1234567890        |
  """

@pytest.mark.version('>=3.0.3')
def test_core_5569_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

