#coding:utf-8
#
# id:           bugs.core_2455
# title:        Server fails when doing DROP DATABASE right after error in statistical fnction
# decription:   
# tracker_id:   CORE-2455
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='ISO8859_1', sql_dialect=3, init=init_script_1)

test_script_1 = """
    commit;
    create database 'localhost:$(DATABASE_LOCATION)trucks';

    set term ^;
    create procedure factorial (
        max_rows integer,
        mode integer )
    returns (
        row_num integer, 
        result integer 
    ) as
        declare variable temp integer;
        declare variable counter integer;
    begin
      counter=0;
      temp=1;
      while (counter <= max_rows) do 
      begin
        row_num = counter;

        if ( row_num = 0 ) then
            temp = 1;
        else
            temp = temp * row_num;
        
        result = temp;
        counter = counter + 1;

        if (mode=1) then 
            suspend;
      end

      if (mode = 2) then 
          suspend;
    end
    ^
    set term ; ^
    commit;

    set list on;

    select 0 as run_no, sp.* from factorial(5,2) sp;

    create table onerow (i integer);
    insert into onerow values (5);

    -- note the derived table query
    select 
        1 as run_no
       ,(select ROW_NUM from factorial(i,2)) as RN 
    from onerow ;

    select 
        2 as run_no
       ,(select RESULT from factorial(i,2)) as RS 
    from onerow ;

    -- note the derived table query
    select 3 as run_no, (select ROW_NUM from factorial(i,1)) as RN from onerow ;
    select 4 as run_no, (select RESULT from factorial(i,1)) as RS from onerow ;

    drop database ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RUN_NO                          0
    ROW_NUM                         5
    RESULT                          120
    RUN_NO                          1
    RN                              5
    RUN_NO                          2
    RS                              120
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 21000
    multiple rows in singleton select
    Statement failed, SQLSTATE = 21000
    multiple rows in singleton select
  """

@pytest.mark.version('>=2.5')
def test_core_2455_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

