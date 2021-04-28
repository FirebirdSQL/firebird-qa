#coding:utf-8
#
# id:           functional.tabloid.join_on_position_function_result
# title:        Records with NULLs could be lost from resultset.
# decription:   
#                    http://www.sql.ru/forum/actualutils.aspx?action=gotomsg&tid=1009792&msg=14032086
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table t(id int, s varchar(30));
    commit;
    insert into t values(1, 'aaa');
    insert into t values(11, 'bbb');
    insert into t values(111, 'ccc');
    insert into t values(12, 'ddd');
    insert into t values(123, 'eee');
    insert into t values(1234, 'fff');
    commit;

    set list on;
    select t.id, t.s, x.p, position(','||cast(t.id as varchar(11))||',', x.p) k
    from t
      left join (select ',123,12,11,' p from rdb$database) x
      on position(','||cast(t.id as varchar(11))||',', x.p)>0
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    S                               aaa
    P                               <null>
    K                               <null>
    ID                              11
    S                               bbb
    P                               ,123,12,11,
    K                               8
    ID                              111
    S                               ccc
    P                               <null>
    K                               <null>
    ID                              12
    S                               ddd
    P                               ,123,12,11,
    K                               5
    ID                              123
    S                               eee
    P                               ,123,12,11,
    K                               1
    ID                              1234
    S                               fff
    P                               <null>
    K                               <null>
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

