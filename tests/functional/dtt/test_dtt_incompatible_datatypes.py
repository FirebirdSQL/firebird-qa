#coding:utf-8

"""
ID:          n/a
ISSUE:       https://groups.google.com/g/firebird-devel/c/TfMzdpsTHpg/m/OmDoMyXFAQAJ
TITLE:       DECLARED TEMPORARY TABLE. Bugcheck when running core with incomatible data types
DESCRIPTION:
    Before fix message "consistency check (record disappeared (186), file: Savepoint.cpp line: 281)" did appear in the server log.
    Fix: https://github.com/FirebirdSQL/firebird/commit/5a1ea99bd94412cdf711d9a177377f7107b78fff
NOTES:
    [29.07.2026] pzotov
    Problem found in 6.0.0.2092-3fa7269
    Checked on 6.0.0.2100-5a1ea99.
"""
import locale
from difflib import unified_diff
import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' '), ('(-)?At block.*', '')]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    test_script = """
        set bail on;
        set list on;
        set autoterm on;
        create domain dm_rdb_key char(8) character set octets;
        commit;
        execute block returns (
            local_proc_result boolean
        ) as
            declare procedure local_sp returns(local_proc_result dm_rdb_key) as
                declare local temporary table dtt_inner (
                    fn boolean
                );
            begin
                insert into dtt_inner values (false) returning not fn into local_proc_result;
                suspend;
            end
        begin
            -- Before fix bugcheck was here with following in firebird.log:
            -- conversion error from string "TRUE#x00#x00#x00#x00"
        	-- At block line: 48, col: 5
        	-- internal Firebird consistency check (record disappeared (186), file: Savepoint.cpp line: 281)
            execute procedure local_sp returning_values local_proc_result;
            suspend;
        end;
    """

    # Get content of firebird.log BEFORE running test sql:
    log_before = act.get_firebird_log()
    

    expected_stdout = """
        Statement failed, SQLSTATE = 22018
        conversion error from string "TRUE#x00#x00#x00#x00"
    """

    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input = test_script, combine_output = True, io_enc = locale.getpreferredencoding())
    # DO NOT: assert act.clean_stdout == act.clean_expected_stdout -- we have also to check firebird.log diff, see below.

    if act.clean_stdout == act.clean_expected_stdout:
        pass
    else:
        isql_diff = unified_diff(act.clean_expected_stdout.splitlines(), act.clean_stdout.splitlines())
        if isql_diff:
            print('UNEXPECTED difference in ISQL output:')
            for line in isql_diff:
                print(f'{line}')
    act.reset()

    #-----------------------------------------------------------------------

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
