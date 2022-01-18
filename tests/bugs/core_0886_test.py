#coding:utf-8

"""
ID:          issue-1279
ISSUE:       1279
TITLE:       SPs in views
DESCRIPTION:
JIRA:        CORE-886
"""

import pytest
from firebird.qa import *

init_script = """set term !!;
create procedure MY_PROCEDURE (input1 INTEGER)
returns (output1 INTEGER)
as begin
 output1 = input1+1;
 suspend;
end !!
set term ;!!
commit;

"""

db = db_factory(init=init_script)

test_script = """create view a_view as
select * from MY_PROCEDURE(1);
commit;
show view a_view;
select *from a_view;
"""

act = isql_act('db', test_script)

expected_stdout = """Database:  test.fdb, User: SYSDBA
SQL> CON> SQL> SQL> OUTPUT1                         INTEGER Nullable
View Source:
==== ======

select * from MY_PROCEDURE(1)
SQL>
     OUTPUT1
============
           2

SQL> SQL>"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

