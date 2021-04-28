#coding:utf-8
#
# id:           bugs.core_3834
# title:        Usage of a NATURAL JOIN with a derived table crashes the server
# decription:   
# tracker_id:   CORE-3834
# min_versions: ['2.5.2']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core3834.fbk', init=init_script_1)

test_script_1 = """
    set planonly;
    select r.revision 
    from ( select r.revision, r.stageid from tilemaps r ) r 
    natural join logs g 
    where stageid = ?
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN HASH (G NATURAL, R R NATURAL)
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

