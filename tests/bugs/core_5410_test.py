#coding:utf-8
#
# id:           bugs.core_5410
# title:        Dependencies are not stored when using some type of contructions in subroutines
# decription:   
#                  Confirmed:
#                  1) bug on WI-V3.0.2.32630, WI-T4.0.0.454
#                  2) fixed on WI-V3.0.2.32642, WI-T4.0.0.460 (does not allow to drop tables).
#                
# tracker_id:   CORE-5410
# min_versions: ['3.0.2']
# versions:     3.0.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    create or alter procedure sp_outer_standalone as begin end;
    create or alter package pg_test as begin end;
    commit;

    recreate table test_1(f01 integer);
    insert into test_1(f01) values(100);
    insert into test_1(f01) values(1);
    insert into test_1(f01) values(10);
    commit;

    recreate table test_2(f02 integer);
    commit;
    insert into test_2(f02) values(200);
    insert into test_2(f02) values(2);
    insert into test_2(f02) values(20);
    commit;

    recreate table test_3(f02 integer);
    commit;
    insert into test_3(f02) values(300);
    insert into test_3(f02) values(3);
    insert into test_3(f02) values(30);
    commit;

    set term ^;
    create or alter procedure sp_outer_standalone returns(max_f01 int) as
        declare procedure sp_inner returns(max_f01 int) as
        begin
            select max(f01) from test_1 into max_f01;
            suspend;
        end
    begin
        select max_f01 from sp_inner into max_f01;
        suspend;
    end;
    ^

    create or alter function fn_outer_standalone returns int as
        declare function fn_inner returns int as
        begin
            return (select min(f01) from test_1);
        end
    begin
        return fn_inner();
    end;
    ^

    create or alter package pg_test as 
    begin
        procedure sp_outer_packaged returns(max_f02 int);
        function fn_outer_packaged returns int;
    end
    ^
    recreate package body pg_test as
    begin
        procedure sp_outer_packaged returns(max_f02 int) as
            declare procedure sp_inner returns(max_f02 int) as
            begin
                select max(f02) from test_2 into max_f02;
                suspend;
            end
        begin
            select max_f02 from sp_inner into max_f02;
            suspend;
        end

        function fn_outer_packaged returns int as
            declare function fn_inner returns int as
            begin
                return (select min(f02) from test_2);
            end
        begin
            return fn_inner();
        end
    end
    ^

    set term ;^
    commit;

    -----------------------

    drop table test_1; -- should FAIL!
    drop table test_2; -- should FAIL!
    commit;

    select max_f01 from sp_outer_standalone;
    select fn_outer_standalone() as min_f01 from rdb$database;

    select max_f02 from pg_test.sp_outer_packaged;
    select pg_test.fn_outer_packaged() as min_f02 from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MAX_F01                         100
    MIN_F01                         1

    MAX_F02                         200
    MIN_F02                         2

  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN TEST_1.F01
    -there are 2 dependencies

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN TEST_2.F02
    -there are 1 dependencies
  """

@pytest.mark.version('>=3.0.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

