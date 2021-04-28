#coding:utf-8
#
# id:           bugs.core_1750
# title:        Include information about context variables into the monitoring tables
# decription:   
# tracker_id:   CORE-1750
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
	set count on;
	select mon$variable_name, mon$variable_value from mon$context_variables;
	commit;
	set term ^;
	execute block as
	    declare c int;
	begin
	    c = rdb$set_context('USER_SESSION', 'SESSION_LEVEL_VARIABLE', 1);
	end
	^
	commit
	^
	execute block as
	    declare c int;
	begin
	    c = rdb$set_context('USER_TRANSACTION', 'TRANSACTION_LEVEL_VARIABLE', 1);
	end
	^
	select mon$variable_name, mon$variable_value from mon$context_variables
	^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	Records affected: 0

	MON$VARIABLE_NAME               SESSION_LEVEL_VARIABLE
	MON$VARIABLE_VALUE              1
	MON$VARIABLE_NAME               TRANSACTION_LEVEL_VARIABLE
	MON$VARIABLE_VALUE              1
	
	Records affected: 2  
  """

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

