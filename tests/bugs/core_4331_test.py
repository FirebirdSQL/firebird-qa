#coding:utf-8
#
# id:           bugs.core_4331
# title:        LAG, LEAD and NTH_VALUE raise error when the second argument is NULL
# decription:   
# tracker_id:   CORE-4331
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
	recreate table test(id int primary key, x int, y int);
	commit;
	insert into test values(101, 1, 10);
	insert into test values(102, 2, 20);
	insert into test values(103, 3, 30);
	insert into test values(104, 4, 40);
	insert into test values(105, 5, 50);
	insert into test values(106, 6, 60);
	insert into test values(107, 7, 70);
	commit;

	set list on;
	select 
		 id
		,lag(x,null)over(order by id) x_lag
		,lead(x,null)over(order by id) x_lead
		,nth_value(x,null)over(order by id) x_nth
	from test t
	order by id;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	ID                              101
	X_LAG                           <null>
	X_LEAD                          <null>
	X_NTH                           <null>

	ID                              102
	X_LAG                           <null>
	X_LEAD                          <null>
	X_NTH                           <null>

	ID                              103
	X_LAG                           <null>
	X_LEAD                          <null>
	X_NTH                           <null>

	ID                              104
	X_LAG                           <null>
	X_LEAD                          <null>
	X_NTH                           <null>

	ID                              105
	X_LAG                           <null>
	X_LEAD                          <null>
	X_NTH                           <null>

	ID                              106
	X_LAG                           <null>
	X_LEAD                          <null>
	X_NTH                           <null>

	ID                              107
	X_LAG                           <null>
	X_LEAD                          <null>
	X_NTH                           <null>
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

