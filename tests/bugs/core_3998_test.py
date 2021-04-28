#coding:utf-8
#
# id:           bugs.core_3998
# title:        Parametrized execute statement fails
# decription:   
# tracker_id:   CORE-3998
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """
	create table t (
		id integer not null,
		dir varchar(100) default '' not null,
		note varchar(100) default '' not null
	);
	commit;
	insert into t (id, dir, note) values (1, 'a', 'b');
	commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
	set term ^;
	execute block
	as
	  declare variable dir varchar(100);
	  declare variable note varchar(100);
	  declare variable id integer;
	begin
	  id = 1;
	  dir = 'a';
	  note = 'bbbb';

	  execute statement ('
		update t set
		  note = :note
		where
		  id = :id and dir = :dir
	  ')
	  (
		id := :id,
		note := :note,
		dir := :dir
	  );
	end ^
	set term ;^
	commit;
	set list on;
	select * from t;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	ID                              1
	DIR                             a
	NOTE                            bbbb  
  """

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

