#coding:utf-8
#
# id:           bugs.core_6145
# title:        Wrong result in "similar to" with non latin characters
# decription:   
#               	Confirmed bug on 4.0.0.1607
#               	Checked on:
#               		4.0.0.1614: OK, 1.509s.
#               		3.0.5.33171: OK, 0.682s.
#               		2.5.9.27142: OK, 0.629s.	
#                
# tracker_id:   CORE-6145
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    set count on;
	set heading off;
	select 1 from rdb$database where 'я' similar to '%Я%'; 
	select 2 from rdb$database where 'Я' similar to '%я%'; 
	select 3 from rdb$database where 'я' similar to '[Яя]'; 
    select 4 from rdb$database where 'Я' similar to 'я';
    select 5 from rdb$database where 'Я' similar to 'Я';
    select 6 from rdb$database where 'Я' similar to '[яЯ]';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	Records affected: 0
	
	Records affected: 0
	
	3
	Records affected: 1
	
	Records affected: 0
	
	5
	Records affected: 1
	
	6
	Records affected: 1  
  """

@pytest.mark.version('>=2.5')
@pytest.mark.platform('Windows')
def test_core_6145_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

