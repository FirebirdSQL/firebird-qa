#coding:utf-8
#
# id:           bugs.core_5871
# title:        Incorrect caching of the subquery result (procedure call) in independent queries
# decription:   
#                  Beside stanalone stored procedure it was decided to check also stored function, and packaged SP and func.
#                  Checked on: FB40SS, build 4.0.0.1143: OK, 2.219s.
#                
# tracker_id:   CORE-5871
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create or alter procedure p1 (n int) returns (r int) as
    begin
      r = n;
      suspend;
    end
    ^

    create or alter function f1 (n int) returns int as
      declare r int;
    begin
      r = n;
      return r;
    end
    ^

    create or alter package pkg
    as
    begin
        procedure pk_p1(n int) returns(r int);
        function pk_f1(n int) returns int;
    end
    ^

    recreate package body pkg
    as
    begin
        procedure pk_p1(n int) returns(r int) as
        begin
          r = n;
          suspend;
        end

        function pk_f1(n int) returns int as
          declare r int;
        begin
          r = n;
          return r;
        end
    end
    ^

    --------------------------------------------------------------------------------


    create or alter procedure sp_test returns ( s1 varchar(100), s2 varchar(100), s3 varchar(100), s4 varchar(100) ) as
      declare i int;
    begin
      i = 0;
      while (i < 3) do
      begin
        i = i + 1;

        select
          (select
             coalesce(:s1, '') || ' ' || :i || '=' || (select r from p1(:i))
             from rdb$database
          )
          from rdb$database
        into s1;

        select
          (
             select
             coalesce(:s2, '') || ' ' || :i || '=' || ( select f1(:i) from rdb$database )
             from rdb$database
          )
          from rdb$database
        into s2;


        select
          (select
             coalesce(:s3, '') || ' ' || :i || '=' || (select r from pkg.pk_p1(:i))
             from rdb$database
          )
          from rdb$database
        into s3;

        select
          (
             select
             coalesce(:s4, '') || ' ' || :i || '=' || ( select pkg.pk_f1(:i) from rdb$database )
             from rdb$database
          )
          from rdb$database
        into s4;
        
      
      end
      suspend;
    end
    ^
    set term ;^
    commit;

    set list on;
    select * from sp_test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    S1                               1=1 2=2 3=3
    S2                               1=1 2=2 3=3
    S3                               1=1 2=2 3=3
    S4                               1=1 2=2 3=3
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

