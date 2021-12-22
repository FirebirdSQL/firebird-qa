#coding:utf-8
#
# id:           bugs.core_1830
# title:        Possible index corruption with multiply updates of the same record in the same transaction and using of savepoints
# decription:   
# tracker_id:   CORE-1830
# min_versions: []
# versions:     2.5
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('column.*', 'column x'), ('[ \t]+', ' '), ('-At block line: [\\d]+, col: [\\d]+', '')]

init_script_1 = """
	create table a(id char(1), name varchar(255));

	create index idx_a on a (id);
	create exception ex_perm 'Something wrong occurs...';
	commit ;

	insert into a (id) values ('1');
	commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
	select * from a where id = '1';
	set term ^;
	execute block as
	begin
	  update a set name = 'xxx';
	  update a set id = '2';
	  exception ex_perm;
	end ^
	set term ; ^
	select * from a ;
	select * from a where id = '1' ;

	commit;
	select * from a ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	ID                              1
	NAME                            <null>
	
	ID                              1
	NAME                            <null>
	
	ID                              1
	NAME                            <null>
	
	ID                              1
	NAME                            <null>  
"""
expected_stderr_1 = """
	Statement failed, SQLSTATE = HY000
	exception 1
	-EX_PERM
	-Something wrong occurs...  
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

