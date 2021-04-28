#coding:utf-8
#
# id:           bugs.core_6251
# title:        Regression: crash when built-in function LEFT() or RIGHT() missed 2nd argument (number of characters to be taken)
# decription:   
#                   Confirmed crash on: 4.0.0.1773; 3.0.6.33247
#                   Checked on: 4.0.0.1779; 3.0.6.33251 - works fine.
#                
# tracker_id:   CORE-6251
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test( s varchar(10) );
    commit;
    insert into test(s) values('1');
    select 1 from test f where right( f.s ) = '1';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 39000
    function RIGHT could not be matched
  """

@pytest.mark.version('>=3.0.6')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

