#coding:utf-8
#
# id:           functional.domain.alter_03
# title:        ALTER DOMAIN - ADD CONSTRAINT
# decription:   
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.domain.alter.alter_domain_03

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = [('RDB\\$VALIDATION_SOURCE.*', '')]

init_script_1 = """
    create domain test varchar(63);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    alter domain test add constraint check (value like 'te%');
    commit;
    set list on;
    set blob all;
    select rdb$field_name, rdb$validation_source from rdb$fields where rdb$field_name=upper('test');  
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$FIELD_NAME                  TEST
    check (value like 'te%')
  """

@pytest.mark.version('>=2.0')
def test_alter_03_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

