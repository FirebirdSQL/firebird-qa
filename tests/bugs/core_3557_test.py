#coding:utf-8
#
# id:           bugs.core_3557
# title:        AV in engine when preparing query against dropping table
# decription:   
# tracker_id:   CORE-3557
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core3557.fbk', init=init_script_1)

test_script_1 = """
    -- Confirmed for 2.5.0 only: server crashes on running the following EB. 26.02.2015
    -- All subsequent releases should produce no stdout & stderr.
    set term ^;
    execute block as
    begin
      execute statement 'drop table t';
      in autonomous transaction do
        execute statement ('insert into t values (1)');
    end
    ^ 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.execute()

