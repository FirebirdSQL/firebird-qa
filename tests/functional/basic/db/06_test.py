#coding:utf-8
#
# id:           functional.basic.db.06
# title:        Empty DB - RDB$FIELD_DIMENSIONS
# decription:   Check for correct content of RDB$FIELD_DIMENSIONS in empty database.
# tracker_id:   
# min_versions: []
# versions:     2.5
# qmid:         functional.basic.db.db_06

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set count on;
    select * from rdb$field_dimensions order by rdb$field_name;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

