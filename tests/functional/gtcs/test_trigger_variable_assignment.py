#coding:utf-8
#
# id:           functional.gtcs.trigger_variable_assignment
# title:        GTCS/tests/CF_ISQL_21. Variable in the AFTER-trigger must be allowed for assignment OLD value in it.
# decription:   
#               	::: NB ::: 
#               	### Name of original test has no any relation with actual task of this test: ###
#                   https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_21.script
#               
#                   AP,2005 - can't assign old.* fields in triggers
#               
#                   Checked on: 4.0.0.1803 SS; 3.0.6.33265 SS; 2.5.9.27149 SC.
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('=', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table u(a int);
    set term ^;
    create trigger trg_u_aid for u after insert or update or delete as 
        declare i int;
    begin
        i = old.a; 
    end^
    commit^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.execute()

