#coding:utf-8
#
# id:           bugs.core_3754
# title:        SIMILAR TO works wrongly
# decription:   See also: sql.ru/forum/actualutils.aspx?action=gotomsg&tid=1026749&msg=14380584
# tracker_id:   CORE-3754
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test_a(id integer, cnt integer);
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    select iif( '1' similar to '(1|2){0,}', 1, 0)as result from rdb$database
    union all
    select iif( '1' similar to '(1|2){0,1}', 1, 0)from rdb$database
    union all
    select iif( '1' similar to '(1|2){1}', 1, 0)from rdb$database
    union all
    select iif( '123' similar to '(1|12[3]?){1}', 1, 0)from rdb$database
    union all
    select iif( '123' similar to '(1|12[3]?)+', 1, 0) from rdb$database
    union all
    select iif( 'qwertyqwertyqwe' similar to '(%qwe%){2,}', 1, 0) from rdb$database
    union all
    select iif( 'qwertyqwertyqwe' similar to '(%(qwe)%){2,}', 1, 0) from rdb$database
    union all
    select iif( 'qqqqqqqqqqqqqqq' similar to '(%q%){2,}', 1, 0) from rdb$database
    ;
    -- BTW: result in WI-T3.0.0.31681 matches to Postgress 9.3, checked 24.02.2015
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    1 
    1 
    1 
    1 
    1 
    1 
    1 
    1 
  """

@pytest.mark.version('>=3.0')
def test_core_3754_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

