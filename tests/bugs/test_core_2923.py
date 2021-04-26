#coding:utf-8
#
# id:           bugs.core_2923
# title:        Problem with dependencies between a procedure and a view using that procedure
# decription:   
# tracker_id:   CORE-2923
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create procedure sp_test returns (i smallint) as 
    begin 
        i = 32767;
        suspend; 
    end
    ^

    create view v0 as 
    select i 
    from sp_test
    ^

    alter procedure sp_test returns (i int) as 
    begin 
        i = 32768;
        suspend; 
    end
    ^
    set term ;^
    commit;

    ---

    create table t1 (n1 smallint);

    insert into t1(n1) values(32767);
    commit;

    create view v1 as 
    select * 
    from t1;

    alter table t1 alter n1 type integer; 
    commit;

    insert into t1(n1) values(32768);
    commit;

    ---

    create table t2 (n2 smallint);

    insert into t2(n2) values(32767);
    commit;

    create domain d2 integer;

    create view v2 as 
    select * from t2;

    alter table t2 alter n2 type d2; 

    insert into t2(n2) values(32768);
    commit;

    ---

    set list on;
    select '0' as test_no, v.* from v0 v
    union all
    select '1', v.* from v1 v
    union all
    select '2', v.* from v2 v
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TEST_NO                         0
    I                               32768
    TEST_NO                         1
    I                               32767
    TEST_NO                         1
    I                               32768
    TEST_NO                         2
    I                               32767
    TEST_NO                         2
    I                               32768
  """

@pytest.mark.version('>=3.0')
def test_core_2923_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

