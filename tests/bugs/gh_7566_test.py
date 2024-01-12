#coding:utf-8

"""
ID:          issue-7566
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7566
TITLE:       Allow DEFAULT keyword in argument list
NOTES:
    [12.01.2024] pzotov
    Checked on 6.0.0.207
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set term ^;
    create or alter procedure sp_test (
         a_1 int default 1
        ,a_2 int default 2
        ,a_3 int default 3
        ,a_4 int default 4
        ,a_5 int default 5
    ) returns( o_sum int ) as
    begin
        o_sum = a_1 + a_2 + a_3 + a_4+ a_5;
        suspend;
    end
    ^
    create or alter function fn_test (
         a_1 int default 1
        ,a_2 int default 2
        ,a_3 int default 3
        ,a_4 int default 4
        ,a_5 int default 5
    ) returns int as
    begin
        return a_1 + a_2 + a_3 + a_4+ a_5;
    end
    ^

    create or alter package pg_test as
    begin
        procedure sp(a_1 int default 1, a_2 int default 2, a_3 int default 3, a_4 int default 4, a_5 int default 5) returns(o_sum int);
        function fn(a_1 int default 1, a_2 int default 2, a_3 int default 3, a_4 int default 4, a_5 int default 5) returns int;
    end
    ^

    recreate package body pg_test as
    begin
        -- Statement failed, SQLSTATE = 42000
        -- unsuccessful metadata update
        -- -RECREATE PACKAGE BODY PG_TEST failed
        -- procedure sp(a_1 int default 1, a_2 int default 2, a_3 int default 3, a_4 int default 4, a_5 int default 5) returns(o_sum int) as
        procedure sp(a_1 int, a_2 int, a_3 int, a_4 int, a_5 int) returns(o_sum int) as
        begin
            o_sum = a_1 + a_2 + a_3 + a_4 + a_5;
            suspend;
        end

        -- function fn(a_1 int default 1, a_2 int default 2, a_3 int default 3, a_4 int default 4, a_5 int default 5) returns int as
        function fn(a_1 int, a_2 int, a_3 int, a_4 int, a_5 int) returns int as
        begin
            return a_1 + a_2 + a_3 + a_4+ a_5;
        end
    end
    ^
    set term ;^
    commit;

    select o_sum as standalone_sp_1 from sp_test;
    select o_sum as standalone_sp_2 from sp_test(default, default, default, default, default);
    select o_sum as standalone_sp_3 from sp_test(default,      -1, default,      -2, default);
    select o_sum as standalone_sp_4 from sp_test(     -1, default, default, default,      -5);

    ----------------------------------

    select fn_test() as standalone_fn_1 from rdb$database;
    select fn_test(default, default, default, default, default) as standalone_fn_2 from rdb$database;
    select fn_test(default,      -1, default,      -2, default) as standalone_fn_3 from rdb$database;
    select fn_test(     -1, default, default, default,      -5) as standalone_fn_4 from rdb$database;

    ----------------------------------

    select o_sum as packaged_sp_1 from pg_test.sp;
    select o_sum as packaged_sp_2 from pg_test.sp(default, default, default, default, default);
    select o_sum as packaged_sp_3 from pg_test.sp(default,      -1, default,      -2, default);
    select o_sum as packaged_sp_4 from pg_test.sp(     -1, default, default, default,      -5);

    select pg_test.fn() as packaged_fn_1 from rdb$database;
    select pg_test.fn(default, default, default, default, default) as packaged_fn_2 from rdb$database;
    select pg_test.fn(default,      -1, default,      -2, default) as packaged_fn_3 from rdb$database;
    select pg_test.fn(     -1, default, default, default,      -5) as packaged_fn_4 from rdb$database;

"""

act = isql_act('db', test_script)

expected_stdout = """
    STANDALONE_SP_1                 15
    STANDALONE_SP_2                 15
    STANDALONE_SP_3                 6
    STANDALONE_SP_4                 3
    STANDALONE_FN_1                 15
    STANDALONE_FN_2                 15
    STANDALONE_FN_3                 6
    STANDALONE_FN_4                 3
    PACKAGED_SP_1                   15
    PACKAGED_SP_2                   15
    PACKAGED_SP_3                   6
    PACKAGED_SP_4                   3
    PACKAGED_FN_1                   15
    PACKAGED_FN_2                   15
    PACKAGED_FN_3                   6
    PACKAGED_FN_4                   3
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
