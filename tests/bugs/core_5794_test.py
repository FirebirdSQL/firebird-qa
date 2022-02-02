#coding:utf-8

"""
ID:          issue-6057
ISSUE:       6057
TITLE:       Wrong behavour FOR <select_stmt> [AS CURSOR cursorname] with next update and delete
DESCRIPTION:
  Despite that this ticket was closed with solution "Won't fix" i see that it is useful for additional
  checking of cursor stability feature (new in 3.0).
  See also:
  1) test for #3728 (CORE-3362)
  2) comment in this ticket (CORE-5794) by hvlad:
  "Since Firebird3 <..> cursor doesn't see the changes made by "inner" statements."
JIRA:        CORE-5794
FBTEST:      bugs.core_5794
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
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

act = isql_act('db', test_script, substitutions=[('line:\\s[0-9]+,', 'line: x'),
                                                 ('col:\\s[0-9]+', 'col: y')])

expected_stdout = """
    CTX_VAR                         TRIGGER_OLD_ID
    CTX_VALUE                       1

    CTX_VAR                         TRIGGER_OLD_VAL
    CTX_VALUE                       10
"""

expected_stderr = """
    Statement failed, SQLSTATE = HY000
    exception 1
    -TEST_EXCEPTION
    -it is forbidden to delete row with val>0 (id = 1, val=10)
    -At trigger 'TEST_TABLE_BD' line: 6, col: 9
    At block line: 16, col: 9
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
