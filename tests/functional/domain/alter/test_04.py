#coding:utf-8
#
# id:           functional.domain.alter.04
# title:        ALTER DOMAIN - DROP CONSTRAINT
# decription:   
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.domain.alter.alter_domain_04

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """
    create domain test varchar(63) check(value like 'te%');
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    alter domain test drop constraint;
    commit;
    select rdb$field_name, rdb$validation_source
    from rdb$fields
    where rdb$field_name = upper('test');
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$FIELD_NAME                  TEST
    RDB$VALIDATION_SOURCE           <null>
"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

