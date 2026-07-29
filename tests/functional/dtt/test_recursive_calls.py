#coding:utf-8

"""
ID:          n/a
ISSUE:       https://groups.google.com/g/firebird-devel/c/Y4sPSRXSsRQ/m/utHqMUTxAQAJ
TITLE:       DECLARED TEMPORARY TABLE. Bugcheck when recursive calls are used and integer overflow occurs
DESCRIPTION:
    Test verifies that:
        1) declared temporary table name has priority over GTT with same name inside PSQL code;
        2) recursive call of procedure with DTT does NOT allow to see rows in this table that were added/changed in previous levels
           (see doc: "Recursive calls reuse the same compiled table structure, but each recursive execution frame has separate rows")
    Also, test verifies that no bugcheck occurs during evaluating that fails with integer overflow (firebird.log is checked).

    Before fix message "consistency check (record disappeared (186), file: Savepoint.cpp line: 281)" did appear in the server log.
    Fix: https://github.com/FirebirdSQL/firebird/commit/5a1ea99bd94412cdf711d9a177377f7107b78fff
NOTES:
    [29.07.2026] pzotov
    Problem found in 6.0.0.2097-0592438
    Checked on 6.0.0.2100-5a1ea99.
"""
import locale
from difflib import unified_diff
import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' '), ('(-)?At procedure.*', 'At procedure')]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    test_script = """
        set bail on;
        set list on;
        set autoterm on;

        -- Only to check that inside PSQL code declared LOCAL table with same name will be used rather than this GTT:
        create global temporary table t_accumulator(id smallint, f int128) on commit delete rows;

        -- CHECK #1:
        -- #########
        create or alter procedure sp_recur_chk(i smallint) returns(f_via_recursive_sp_calls int128, f_via_accumulator_table int128) as
            -- "Unqualified references to the declared name resolve to the declared local table"
            -- Following declaration makes code to use THIS local table instead of GTT with same name.
            -- This priority can be checked by comparison of f_via_recursive_sp_calls vs f_via_accumulator_table: they must be equal.
            -- If we comment out this declaration (and thus GTT will be used) then f_via_accumulator_table will be GREATER then correct result.
            declare temporary table t_accumulator(id smallint, f int128); --- [ 1 ]
        begin
            if ( i > 1 ) then
                begin
                    f_via_recursive_sp_calls = i * (select f_via_recursive_sp_calls from sp_recur_chk( :i - 1 ));
                end
            else
                begin
                    f_via_recursive_sp_calls = i;
                end

            insert into t_accumulator(id, f) values(:i, :f_via_recursive_sp_calls);
            f_via_accumulator_table = (select sum(f) from t_accumulator);
            suspend;

        end
        ;
        -- must show two equal results:
        select p.* from sp_recur_chk(33) p;

        ------------------------------------------------------------------------------------
        -- CHECK #2:
        -- #########
        create or alter procedure sp_recur_ovf(i smallint) returns(f_via_recursive_sp_calls int128, f_via_accumulator_table int128) as
            declare temporary table t_accumulator(id smallint, f int128);
        begin
            if ( i > 1 ) then
                begin
                    f_via_recursive_sp_calls = i * (select f_via_recursive_sp_calls from sp_recur_ovf( :i - 1 ));
                end
            else
                begin
                    f_via_recursive_sp_calls = i;
                end

            insert into t_accumulator(id, f) values(:i, :f_via_recursive_sp_calls);
            f_via_accumulator_table = (select sum(f) from t_accumulator);
            suspend;

        end
        ;

        -- Before fix there was bugheck with "SQLSTATE = 08006 / Error reading data from the connection"
        -- Now it must raise "SQLSTATE = 22003 / ... numeric overflow ... / -Integer overflow. ...":
        select p.* from sp_recur_ovf(34) p;
    """

    expected_stdout = """
        F_VIA_RECURSIVE_SP_CALLS 8683317618811886495518194401280000000
        F_VIA_ACCUMULATOR_TABLE  8683317618811886495518194401280000000

        Statement failed, SQLSTATE = 22003
        arithmetic exception, numeric overflow, or string truncation
        -Integer overflow. The result of an integer operation caused the most significant bit of the result to carry.
        -At procedure "PUBLIC"."SP_RECUR_OVF" line: 7, col: 21
    """

    # Get content of firebird.log BEFORE running test sql:
    log_before = act.get_firebird_log()
    
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
