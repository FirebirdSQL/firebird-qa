#coding:utf-8
#
# id:           bugs.core_5216
# title:        Provide location context (line/column numbers) for runtime errors raised inside EXECUTE BLOCK
# decription:   
#                  Checked on 4.0.0.372, 3.0.1.32598 - works fine.
#                  NOTE: 2.5.x does not work as expected: some of 'line: ..., col: ...' messages are not displayed.
#                
# tracker_id:   CORE-5216
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('exception [\\d]+', 'exception K'), ('At line [\\d]+, column [\\d]+', 'At line N, column M'), ('-At block line: [\\d]+, col: [\\d]+', 'At block line: N, col: M')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate exception rio 'Exception w/o parameter test. Invalid value detected';
    recreate exception foo 'Exception with parameter test. Invalid value of BAR = @1';
    recreate table test(id int constraint test_pk primary key using index test_pk, x int not null, y int not null);
    commit;
    insert into test(id, x, y) values(1, 100, 200);
    commit;

    set term ^;

    
    --  -Column unknown
    --  -NON_EXISTING_COLUMN
    execute block as
    begin
        execute statement 'select non_existing_column from rdb$database';
    end 
    ^


    --  arithmetic exception, numeric overflow, or string truncation
    --  -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.
    execute block as
    begin
        execute statement (
            'execute block(a int = ?) as '
            || 'begin '
            || '  update test set x = x/:a; '
            || 'end') (0);
    end
    ^

    --  Statement failed, SQLSTATE = 42000
    --  validation error for variable R, value "*** null ***"
    execute block as
    begin
        execute statement
            '
            execute block as 
                declare r smallint not null;
            begin 
                execute statement ''select null from rdb$database'' into r;
            end
            '
        ;
    end 
    ^
    
    --  Statement failed, SQLSTATE = 23000
    --  validation error for column "TEST"."X", value "*** null ***"
    execute block as
    begin
        execute statement
            '
            execute block as 
                declare x smallint;
            begin 
                execute statement 
                ''
                    execute block as 
                    begin 
                        update test set x=null; 
                    end
                '';
            end
            '
        ;
    end 
    ^
    

    --  Statement failed, SQLSTATE = 23000
    --  validation error for column "TEST"."Y", value "*** null ***"
    execute block as
    begin
        execute statement
            '
            execute block as 
                declare x smallint;
            begin 
                execute statement 
                ''
                    execute block as
                        declare x smallint; 
                    begin 
                        insert into test(id, x) values(2, 222); 
                    end
                '';
            end
            '
        ;
    end 
    ^
    

    --  Statement failed, SQLSTATE = 23000
    --  violation of PRIMARY or UNIQUE KEY constraint "TEST_PK" on table "TEST"
    --  -Problematic key value is ("ID" = 1)
    execute block as
    begin
        execute statement
            '
            execute block as 
                declare x smallint;
            begin 
                execute statement 
                ''
                    execute block as 
                        declare x smallint; 
                    begin 
                        execute statement 
                        ''''
                            execute block returns(x smallint) as 
                            begin 
                                insert into test(id, x, y) values(1, 200, 400) returning x into x; 
                                suspend; 
                            end
                        '''' into x; 
                    end
                '';
            end
            '
        ;
    end 
    ^

    --  -RIO
    --  -Exception w/o parameter test. Invalid value detected
    execute block as
    begin
        execute statement
            '
            execute block as 
                declare x smallint;
            begin 
                execute statement 
                ''
                    execute block as 
                        declare x smallint; 
                    begin execute statement 
                    ''''
                        execute block as 
                            declare x smallint = 789; 
                        begin
                            x = x * 100;
                        when any do
                            begin
                                exception rio; 
                            end
                        end
                    '''' into x; end
                '';
            end
            '
        ;
    end 
    ^

    --  -FOO
    --  -Exception with parameter test. Invalid value of BAR = *** null ***
    execute block as
    begin
        execute statement
            '
            execute block as 
                declare x smallint;
            begin 
                execute statement 
                ''
                    execute block as 
                        declare x smallint; 
                        begin 
                            execute statement 
                            ''''
                                execute block as 
                                    declare x smallint;
                                begin
                                    x = 99999;
                                when any do
                                    begin
                                        exception foo using(:x); 
                                    end
                                end
                            '''' 
                            into x; 
                        end
                '';
            end
            '
        ;
    end 
    ^

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -NON_EXISTING_COLUMN
    -At line 1, column 8
    -At block line: 3, col: 9

    Statement failed, SQLSTATE = 22012
    arithmetic exception, numeric overflow, or string truncation
    -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.
    -At block line: 1, col: 37
    -At block line: 3, col: 9

    Statement failed, SQLSTATE = 42000
    validation error for variable R, value "*** null ***"
    -At block line: 5, col: 17
    -At block line: 3, col: 9

    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."X", value "*** null ***"
    -At block line: 4, col: 25
    -At block line: 5, col: 17
    -At block line: 3, col: 9

    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."Y", value "*** null ***"
    -At block line: 5, col: 25
    -At block line: 5, col: 17
    -At block line: 3, col: 9

    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "TEST_PK" on table "TEST"
    -Problematic key value is ("ID" = 1)
    -At block line: 4, col: 33
    -At block line: 5, col: 25
    -At block line: 5, col: 17
    -At block line: 3, col: 9

    Statement failed, SQLSTATE = HY000
    exception 55
    -RIO
    -Exception w/o parameter test. Invalid value detected
    -At block line: 8, col: 33
    -At block line: 4, col: 27
    -At block line: 5, col: 17
    -At block line: 3, col: 9

    Statement failed, SQLSTATE = HY000
    exception 56
    -FOO
    -Exception with parameter test. Invalid value of BAR = *** null ***
    -At block line: 8, col: 41
    -At block line: 5, col: 29
    -At block line: 5, col: 17
    -At block line: 3, col: 9
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

