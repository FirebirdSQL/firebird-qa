#coding:utf-8

"""
ID:          issue-3348
ISSUE:       3348
TITLE:       Wrong results or unexpected errors while sorting a large data set
DESCRIPTION:
JIRA:        CORE-2966
"""

import pytest
from firebird.qa import *

init_script = """create table t (col varchar(32000));
commit;
set term !!;
execute block
as
  declare variable i integer;
begin
  i=0;
  while (i < 200000) do begin
    insert into t (col) values(mod(:i, 10));
    i= i+1;
  end
end!!
set term ;!!
commit;"""

db = db_factory(init=init_script)

test_script = """select col from t group by 1;
select cast(col as integer) from t group by 1;
"""

act = isql_act('db', test_script, substitutions=[('=.*', '=')])

expected_stdout = """
COL
===============================================================================
0
1
2
3
4
5
6
7
8
9


        CAST
============
           0
           1
           2
           3
           4
           5
           6
           7
           8
           9

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

