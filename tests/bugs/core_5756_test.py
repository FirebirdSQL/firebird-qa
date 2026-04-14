#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/6019
TITLE:       Regression: FB crashes when trying to recreate table that is in use by DML (3.0.3; 3.0.4; 4.0.0)
DESCRIPTION:
JIRA:        CORE-5756
FBTEST:      bugs.core_5756
    [14.04.2026] pzotov
    Refactored: we have to check only that  script finished w/o fatal error that can not be catched in 'when any' block.
    Errors like 'object in use' will be suppressed.
    Test can be considered as passed if output will contain 'MSG OK' message.

    Confirmed crash on 3.0.3.32900 SS/CS; following messages appeared in the firebird.log:
        Access violation. The code attempted to access a virtual address without privilege to do so.
        This exception will cause the Firebird server to terminate abnormally.
        ...
        Error writing data to the connection.
    Checked on 6.0.0.1891; 5.0.4.1808; 4.0.7.3269; 3.0.14.33855.
"""

import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' ')]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=3.0.3')
def test_1(act: Action, capsys):
    
    test_script = """
        set bail on;
        set list on;
        recreate table test(x int);
        commit;
        set transaction no wait;
        insert into test values(1);
        select * from test;
        set term ^;
        execute block as
        begin
            begin
                execute statement 'recreate table test(x int, y int)'
                with autonomous transaction -- this is needed for crash
                ; 
            when any do
                begin
                    -- nop --
                end
            end
        end ^
        set term ;^
        commit;
        select 'OK' as msg from rdb$database;
    """
    act.isql(switches = ['-q'], input = test_script, combine_output = False)

    if act.stdout:
        for line in act.clean_stdout.splitlines():
                print(line)

    if act.stderr:
        for line in act.clean_stderr.splitlines():
                print(line)
    act.reset()

    act.expected_stdout = """
        X   1
        MSG OK
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
