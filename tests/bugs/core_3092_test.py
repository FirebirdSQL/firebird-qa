#coding:utf-8
#
# id:           bugs.core_3092
# title:        ROW_COUNT is not cleared before the singleton INSERT statement
# decription:   
# tracker_id:   CORE-3092
# min_versions: ['2.1.5']
# versions:     2.1.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.5
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """
	CREATE TABLE DELME (
		A INTEGER,
		B INTEGER
	);
	COMMIT;
	INSERT INTO DELME (A, B)
			   VALUES (1, 11);
	INSERT INTO DELME (A, B)
			   VALUES (2, 22);
	INSERT INTO DELME (A, B)
			   VALUES (3, 33);
	COMMIT;
	SET TERM ^;
	create procedure uui
	returns (
		result varchar(250))
	as
	begin
	  result = '';

	  update delme set
		b = 111
		where a = 1;
	  result = result||'update-1 '||row_count||'; ';

	  update delme set
		b = 222
		where a = 2;
	  result = result||'update-2 '||row_count||'; ';

	  insert into delme(a,b)
		values(4,44);
	  result = result||'insert-1 '||row_count||'; ';
	end
	^
	SET TERM ^;
	COMMIT;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    execute procedure uui;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	RESULT                          update-1 1; update-2 1; insert-1 1;  
  """

@pytest.mark.version('>=2.1.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

