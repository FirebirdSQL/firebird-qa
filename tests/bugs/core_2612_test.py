#coding:utf-8
#
# id:           bugs.core_2612
# title:        Connection lost immediatelly after compiling procedure with RPAD system function
# decription:   
# tracker_id:   CORE-2612
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
	set term ^;
	create procedure TEST2 (name varchar(50),spaces integer)
	returns (rname varchar(200))
	as
	begin
	  rname = name || rpad(' ',:spaces,' ');
	  suspend;
	end^
	set term ;^
	commit;
	set list on;
	set count on;
	select rname || 'end' as rname_padded from TEST2 ('test',5);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	RNAME_PADDED                    test     end
	Records affected: 1  
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

