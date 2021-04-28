#coding:utf-8
#
# id:           bugs.core_5794
# title:        Wrong behavour FOR <select_stmt> [AS CURSOR cursorname] with next update and delete
# decription:   
#                  Despite that this ticket was closed with solution "Won't fix" i see that it is useful for additional 
#                  checking of cursor stability feature (new in 3.0).
#                  See also:
#                  1) test for CORE-3362;
#                  2) comment in this ticket (CORE-5794) by hvlad: 
#                  "Since Firebird3 <..> cursor doesn't see the changes made by "inner" statements."
#                
# tracker_id:   CORE-5794
# min_versions: ['3.0.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('line:\\s[0-9]+,', 'line: x'), ('col:\\s[0-9]+', 'col: y')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test_table (
        id integer,
        val integer
    );
    commit;
    insert into test_table (id, val) values (1, 10);
    commit;

    recreate exception test_exception 'test';

    set term ^ ;
    create or alter trigger test_table_bd for test_table active before delete position 0 as
    begin
        rdb$set_context('USER_SESSION','TRIGGER_OLD_ID', coalesce(old.id,'null') );
        rdb$set_context('USER_SESSION','TRIGGER_OLD_VAL', coalesce(old.val,'null') );
        if (old.val >0 ) then 
            exception test_exception 'it is forbidden to delete row with val>0 (id = '||coalesce(old.id, 'null')||', val='||coalesce(old.val,'null')||')';
    end
    ^

    execute block as
        declare curVal integer;
        declare curID integer;
    begin
        for select id, val
        from test_table
        where val>0
        into curid, curval
        as cursor tmpcursor
        do begin
            update test_table
            set val=0
            where current of tmpcursor;
           
            -- NO error in 2.5:
            delete from test_table
            where current of tmpcursor;
        end
    end
    ^
    set term ;^

    set list on;
    select mon$variable_name as ctx_var, mon$variable_value as ctx_value from mon$context_variables;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CTX_VAR                         TRIGGER_OLD_ID
    CTX_VALUE                       1

    CTX_VAR                         TRIGGER_OLD_VAL
    CTX_VALUE                       10
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = HY000
    exception 1
    -TEST_EXCEPTION
    -it is forbidden to delete row with val>0 (id = 1, val=10)
    -At trigger 'TEST_TABLE_BD' line: 6, col: 9
    At block line: 16, col: 9
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

