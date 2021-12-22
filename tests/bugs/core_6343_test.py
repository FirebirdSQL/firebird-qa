#coding:utf-8
#
# id:           bugs.core_6343
# title:        Rolled back transaction produces unexpected results leading to duplicate values in PRIMARY KEY field
# decription:   
#                  Confirmed bug on 3.0.6.33322: duplicates in PK remain after test script.
#                  Checked on 3.0.6.33326 - all fine.
#               
#                  NOTE: 3.0.x only was affected. No such problem in 4.x
#                
# tracker_id:   CORE-6343
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = [('line:.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter procedure sp_test as begin end;

    create global temporary table gtt_table (
        id integer not null
    ) on commit delete rows;

    create table test (
        id integer not null primary key
    );
    set term ^;
    create or alter procedure sp_test returns ( id1 integer)
    as
       declare variable v integer;
    begin
       insert into gtt_table values(1);
       insert into gtt_table values(2);
       insert into gtt_table values(3);

       for
           select id from gtt_table
           into :id1 do
       begin
             insert into test (id) values (:id1);

             -- NOTE: it is mandatory to make "unnecessary" query to rdb$database
             -- in order to reproduce bug. Do not replace it with "pure PSQL".
             for
                 select 1 from rdb$database into :v
             do 
                if (:id1=3) then
                    id1 = 1/0; -- do NOT suppress this exception otherwise bug will not shown

             suspend;

             delete from test;
        end
    end
    ^
    set term ;^
    commit;
    -----------------------------------
    set heading off;
    -- Iteration #1
    select * from sp_test;
    rollback;
    select * from test;


    -- Iteration #2
    select * from sp_test;
    rollback;
    select * from test;


    -- Iteration #3
    select * from sp_test;
    rollback;
    select * from test;


    -- Iteration #4
    select * from sp_test;
    rollback;
    select * from test;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
           1 
           2 

           1 
           2 

           1 
           2 

           1 
           2 
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22012
    arithmetic exception, numeric overflow, or string truncation
    -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.
    -At procedure 'SP_TEST'

    Statement failed, SQLSTATE = 22012
    arithmetic exception, numeric overflow, or string truncation
    -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.
    -At procedure 'SP_TEST'

    Statement failed, SQLSTATE = 22012
    arithmetic exception, numeric overflow, or string truncation
    -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.
    -At procedure 'SP_TEST'

    Statement failed, SQLSTATE = 22012
    arithmetic exception, numeric overflow, or string truncation
    -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.
    -At procedure 'SP_TEST'
"""

@pytest.mark.version('>=3.0.6')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

