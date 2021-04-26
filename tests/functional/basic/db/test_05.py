#coding:utf-8
#
# id:           functional.basic.db.05
# title:        Empty DB - RDB$DEPENDENCIES
# decription:   Check for correct content of RDB$DEPENDENCIES in empty database.
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.basic.db.db_05

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set count on;
    select * from rdb$dependencies
    order by
        rdb$dependent_name
        ,rdb$depended_on_name
        ,rdb$field_name
        ,rdb$dependent_type
        ,rdb$depended_on_type
        ,rdb$package_name -- avail. only for FB 3.0+
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
  """

@pytest.mark.version('>=3.0')
def test_05_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

