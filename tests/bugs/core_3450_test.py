#coding:utf-8
#
# id:           bugs.core_3450
# title:        Inefficient optimization (regression)
# decription:   
#                  ::: NB :::
#                  It seems that we have regression in current 4.0 snapshots (elapsed time more than 10x comparing with 2.5).
#                  Also, 4.0 has different plan comparing with 3.0.
#                  After discuss with dimitr it was decided to commit this test into fbt-repo in order to have constant
#                  reminder about this issue. 
#                  Currently this test should FAIL on 4.0!
#                
# tracker_id:   CORE-3450
# min_versions: ['2.5.7']
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
    create or alter procedure sp_2 as begin end;

    recreate table test_1 (f1 int, f2 int, f3 int);
    create index test_1_f1 on test_1(f1);
    create index test_1_f2 on test_1(f2);
    commit;

    recreate table test_2 (f1 int, f2 int);
    create index test_2_f1 on test_2(f1);
    create index test_2_f2 on test_2(f2);
    commit;

    recreate table test_3 (f1 int);
    create index test_3_f1 on test_3(f1);
    commit;

    set term ^;
    create or alter procedure sp_1 returns (f1 int)
    as begin
      f1=1;
      suspend;
    end
    ^

    create or alter procedure sp_2 as
      declare i int;
      declare t1_lim int = 1000;
      declare t2_lim int = 100;
      declare t3_lim int = 10;
    begin
      i=0;
      while (i<t1_lim) do begin
        i=i+1;
        insert into test_1 values (:i, 1, 3);
      end

      i=0;
      while (i<t2_lim) do begin
        i=i+1;
        insert into test_2 values (:i, 2);
      end

      i=0;
      while (i<t3_lim) do begin
        i=i+1;
        insert into test_3 values (3);
      end
    end
    ^
    set term ;^
    commit;

    execute procedure sp_2;
    commit;

    set statistics index test_1_f1;
    set statistics index test_1_f2;
    set statistics index test_2_f1;
    set statistics index test_2_f2;
    set statistics index test_3_f1;
    commit;

    set planonly;

    select t2.f1
    from test_2 t2
    join test_1 t1 on t1.f1=t2.f1
    join sp_1 p1 on p1.f1=t1.f2
    join test_3 t3 on t3.f1=t1.f3
    where t2.f2=2
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN JOIN (JOIN (P1 NATURAL, T1 INDEX (TEST_1_F2)), T2 INDEX (TEST_2_F1), T3 INDEX (TEST_3_F1))
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

