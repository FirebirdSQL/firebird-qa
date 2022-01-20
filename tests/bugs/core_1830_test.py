#coding:utf-8

"""
ID:          issue-2259
ISSUE:       2259
TITLE:       Possible index corruption with multiply updates of the same record in the same transaction and using of savepoints
DESCRIPTION:
JIRA:        CORE-1830
"""

import pytest
from firebird.qa import *

init_script = """
	create table a(id char(1), name varchar(255));

	create index idx_a on a (id);
	create exception ex_perm 'Something wrong occurs...';
	commit ;

	insert into a (id) values ('1');
	commit;
"""

db = db_factory(init=init_script)

test_script = """
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

act = isql_act('db', test_script,
                 substitutions=[('column.*', 'column x'), ('[ \t]+', ' '),
                                ('-At block line: [\\d]+, col: [\\d]+', '')])

expected_stdout = """
	ID                              1
	NAME                            <null>

	ID                              1
	NAME                            <null>

	ID                              1
	NAME                            <null>

	ID                              1
	NAME                            <null>
"""

expected_stderr = """
	Statement failed, SQLSTATE = HY000
	exception 1
	-EX_PERM
	-Something wrong occurs...
"""

@pytest.mark.version('>=2.5')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

