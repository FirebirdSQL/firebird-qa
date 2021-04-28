#coding:utf-8
#
# id:           bugs.core_0886
# title:        SPs in views
# decription:   
# tracker_id:   CORE-886
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """set term !!;
create procedure MY_PROCEDURE (input1 INTEGER)
returns (output1 INTEGER)
as begin
 output1 = input1+1;
 suspend;
end !!
set term ;!!
commit;

"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """create view a_view as
select * from MY_PROCEDURE(1);
commit;
show view a_view;
select *from a_view;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:btest2	mpugs.core_0886.fdb, User: SYSDBA
SQL> CON> SQL> SQL> OUTPUT1                         INTEGER Nullable
View Source:
==== ======

select * from MY_PROCEDURE(1)
SQL>
     OUTPUT1
============
           2

SQL> SQL>"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

