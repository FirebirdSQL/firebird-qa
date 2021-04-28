#coding:utf-8
#
# id:           bugs.core_3491
# title:        Altering of a TYPE OF COLUMN parameter affects the original column
# decription:   
# tracker_id:   CORE-3491
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """create table aaa (a integer);
commit;
set term !!;
create or alter procedure bbb
returns (b type of column aaa.a)
as
begin
 suspend;
end!!
set term ;!!
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """show table aaa;
set term !!;
create or alter procedure bbb
returns (b varchar(10))
as
begin
 suspend;
end!!
set term ;!!
commit;
show table aaa;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """SQL> A                               INTEGER Nullable
SQL> A                               INTEGER Nullable
"""

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

