#coding:utf-8
#
# id:           bugs.core_2893
# title:        Expression in a subquery may be treated as invariant and produce incorrect results
# decription:   
#                  Confirmed wrong resultset on 2.1.2.18118.
#                  Added sample from core-3031.
#                
# tracker_id:   CORE-2893
# min_versions: ['2.5.7']
# versions:     2.5.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.7
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test_z (c varchar(10));
    commit;

    insert into test_z values (1);
    insert into test_z values (1);
    insert into test_z values (2);
    insert into test_z values (3);
    commit;

    -- From CORE-3031:
    create view v_test (f1, f2, f3) as
    select '1.1', '1.2', '1.3' from rdb$database
    union all
    select '2.1', '2.2', '2.3' from rdb$database
    union all
    select '3.1', '3.2', '3.3' from rdb$database
    ;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set count on;
    set list on;

    select 'Test-1' as msg, t.*
    from (
      select (select case when R.RDB$Relation_ID = 0 then 0 else 1 end from RDB$Database) TypeID
      from RDB$Relations R
      where R.RDB$Relation_ID < 2
    ) t;

    select 'Test-2' as msg, z.c 
    from test_z z 
    where 
        (
          select z.c || '' from rdb$database
        ) = '1'
    ;
    commit;

    -- From CORE-3031:
    select 'Test-3' as msg, t.*
    from (
      select
          t.f1 || '; ' || t.f2 || '; ' || t.f3 as f123_concat,
          (
            select
              '' || t.f3
            from rdb$database
          ) as f3_concat
      from v_test t
    ) t;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             Test-1
    TYPEID                          0
    MSG                             Test-1
    TYPEID                          1
    Records affected: 2
    MSG                             Test-2
    C                               1
    MSG                             Test-2
    C                               1
    Records affected: 2
    MSG                             Test-3
    F123_CONCAT                     1.1; 1.2; 1.3
    F3_CONCAT                       1.3
    MSG                             Test-3
    F123_CONCAT                     2.1; 2.2; 2.3
    F3_CONCAT                       2.3
    MSG                             Test-3
    F123_CONCAT                     3.1; 3.2; 3.3
    F3_CONCAT                       3.3
    Records affected: 3
  """

@pytest.mark.version('>=2.5.7')
def test_core_2893_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

