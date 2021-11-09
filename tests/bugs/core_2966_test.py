#coding:utf-8
#
# id:           bugs.core_2966
# title:        Wrong results or unexpected errors while sorting a large data set
# decription:
# tracker_id:   CORE-2966
# min_versions: ['2.1.6', '2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = [('=.*', '=')]

init_script_1 = """create table t (col varchar(32000));
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

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select col from t group by 1;
select cast(col as integer) from t group by 1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
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

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

