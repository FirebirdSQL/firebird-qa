#coding:utf-8

"""
ID:          n/a
ISSUE:       https://groups.google.com/g/firebird-devel/c/3o-OHhJEOv0/m/MNc_Vs0KBwAJ
TITLE:       DECLARED TEMPORARY TABLE. Bugcheck in Savepoint.cpp after DLTT usage
DESCRIPTION:
    Test runs script from firebird-devel and checks that no new lines will appear in the firebird.log
    Before fix log message "consistency check (record disappeared (186), file: Savepoint.cpp line: 281)" did appear.
    Fix: https://github.com/FirebirdSQL/firebird/commit/3fa72696c0e026efdd3452b6d07c235505285669
NOTES:
    [25.07.2026] pzotov
        1. Test script *does* contain error and can not be compiled -- this was done intentionally.
        2. Lines marked as "[ 1 ]" and "[ 2 ]" must present in the test script to reproduce problem.
    Problem found in 6.0.0.2092-92bad46.
    Checked 6.0.0.2092-3fa7269 -- all fine.
"""
import locale
from difflib import unified_diff
import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' ')]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    test_script = """
        SET BAIL ON; -- [ 1 ]
        set list on;
        set autoterm on;
        commit;

        create or alter procedure sp_test returns(id016 smallint) as
            declare temporary table tbase(id016 smallint);
        begin
            insert into tbase(id016) values(-32768) returning id016 into id016;
            suspend;
        end;

        select p.* from sp_test p; -- [ 2 ]
        execute block returns (execute_block_outcome varbinary(64)) as
        begin
            execute_block_outcome = crypt_hash (blob_append(null) );
            suspend;
        end;
    """

    # Get content of firebird.log BEFORE running test sql:
    log_before = act.get_firebird_log()

    expected_stdout = """
        ID016 -32768
        Statement failed, SQLSTATE = 42000
        Dynamic SQL Error
        -SQL error code = -104
        -Token unknown - line 4, column 67
        -)
    """
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input = test_script, combine_output = True, io_enc = locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()

    # Get content of firebird.log AFTER running test sql: no diff must occur.
    log_after = act.get_firebird_log()
    log_diff = [x for x in unified_diff(log_before, log_after) if x.startswith('+')]
    if log_diff:
        print('UNEXPECTED lines did appear in the firebird.log:')
    for line in log_diff:
        print(f'{line}')

    act.expected_stdout = """
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
