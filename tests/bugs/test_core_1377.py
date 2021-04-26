#coding:utf-8
#
# id:           bugs.core_1377
# title:        Add an ability to change role without reconnecting to database.
# decription:   
# tracker_id:   
# min_versions: ['3.0']
# versions:     3.0
# qmid:         bugs.core_1377

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create role r1377a;
    create role r1377b;
    commit;
    grant r1377a to sysdba;
    grant r1377b to sysdba;
    commit;
    set list on;
    set role r1377a;
    select current_user, current_role from rdb$database;
    set role r1377b;
    select current_user, current_role from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    USER                            SYSDBA
    ROLE                            R1377A
    
    USER                            SYSDBA
    ROLE                            R1377B
  """

@pytest.mark.version('>=3.0')
def test_core_1377_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

