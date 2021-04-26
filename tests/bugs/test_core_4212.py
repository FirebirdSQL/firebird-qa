#coding:utf-8
#
# id:           bugs.core_4212
# title:        Dropping FK on GTT crashes server
# decription:   
# tracker_id:   CORE-4212
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core4212.fbk', init=init_script_1)

test_script_1 = """
--  'database': 'Existing',
--  'database_name': 'core4212-25.fdb',

    set autoddl off;
    commit;
    alter table t2 drop constraint t2_fk; 
    rollback;
    show table t2;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              VARCHAR(8) Nullable
    CONSTRAINT T2_FK:
      Foreign key (ID)    References T1 (ID)
  """

@pytest.mark.version('>=2.5.3')
def test_core_4212_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

