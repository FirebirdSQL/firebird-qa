#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/9130
TITLE:       Index support for Declared LTT - max count of indices per table
DESCRIPTION:
    Test verifies that one may to use DTT with maximal possible indices (currently: 16).
    Check if performed for ascending and descending index separately (execution plan is checked).
NOTES:
    Original commit:
        https://github.com/FirebirdSQL/firebird/commit/f93b6ce7ba148e6185c40a3328ca56686626e2ae

    [31.08.2026] pzotov
    Checked on 20260829_024127-6.0.0.2164-2d371e2.
"""
import pytest
from firebird.qa import *

db = db_factory()

substitutions = [(r'^((?!PLAN \(\"\S+\" INDEX|DTT_COMPOUND_CNT).)*$', ''), ('[ \t]+', ' '), (r'RDB\$PSQL_LTT_\d+', 'RDB_PSQL_LTT') ]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    test_sql = """
        set bail on;
        set list on;
        set autoterm on;
        --set explain on;
        set plan on;
        execute block returns(dtt_compound_cnt_1 int, dtt_compound_cnt_2 int) as
            declare local temporary table dtt_compound_1 (
                f01 bigint
               ,f02 bigint
               ,f03 bigint
               ,f04 bigint
               ,f05 bigint
               ,f06 bigint
               ,f07 bigint
               ,f08 bigint
               ,f09 bigint
               ,f10 bigint
               ,f11 bigint
               ,f12 bigint
               ,f13 bigint
               ,f14 bigint
               ,f15 bigint
               ,f16 bigint
            )
            ascending index dtt_compound_1_asc (
                f01
               ,f02
               ,f03
               ,f04
               ,f05
               ,f06
               ,f07
               ,f08
               ,f09
               ,f10
               ,f11
               ,f12
               ,f13
               ,f14
               ,f15
               ,f16
            )
            ;
            
            declare local temporary table dtt_compound_2 (
                f01 bigint
               ,f02 bigint
               ,f03 bigint
               ,f04 bigint
               ,f05 bigint
               ,f06 bigint
               ,f07 bigint
               ,f08 bigint
               ,f09 bigint
               ,f10 bigint
               ,f11 bigint
               ,f12 bigint
               ,f13 bigint
               ,f14 bigint
               ,f15 bigint
               ,f16 bigint
            )
            descending index dtt_compound_2_dec (
                f01
               ,f02
               ,f03
               ,f04
               ,f05
               ,f06
               ,f07
               ,f08
               ,f09
               ,f10
               ,f11
               ,f12
               ,f13
               ,f14
               ,f15
               ,f16
            )
            ;
        begin
            insert into dtt_compound_1
            select
                i + 1
               ,i + 2
               ,i + 3
               ,i + 4
               ,i + 5
               ,i + 6
               ,i + 7
               ,i + 8
               ,i + 9
               ,i +10
               ,i +11
               ,i +12
               ,i +13
               ,i +14
               ,i +15
               ,i +16
            from generate_series(0, 399) as s(i);
            insert into dtt_compound_1 default values;

            insert into dtt_compound_2
            select * from dtt_compound_1;

            select count(*) from dtt_compound_1
            where
                f01 = 1
                and f02 = 2
                and f03 = 3
                and f04 = 4
                and f05 = 5
                and f06 = 6
                and f07 = 7
                and f08 = 8
                and f09 = 9
                and f10 =10
                and f11 =11
                and f12 =12
                and f13 =13
                and f14 =14
                and f15 =15
                and f16 =16
            into dtt_compound_cnt_1;

            select count(*) from dtt_compound_2
            where
                f01 = 1
                and f02 = 2
                and f03 = 3
                and f04 = 4
                and f05 = 5
                and f06 = 6
                and f07 = 7
                and f08 = 8
                and f09 = 9
                and f10 =10
                and f11 =11
                and f12 =12
                and f13 =13
                and f14 =14
                and f15 =15
                and f16 =16
            into dtt_compound_cnt_2;

            suspend;
        
        end;

    """

    act.expected_stdout = f"""
        PLAN ("RDB_PSQL_LTT" INDEX ("DTT_COMPOUND_1_ASC"))
        PLAN ("RDB_PSQL_LTT" INDEX ("DTT_COMPOUND_2_DEC"))
        DTT_COMPOUND_CNT_1 1
        DTT_COMPOUND_CNT_2 1

    """
    act.isql(switches=['-q'], combine_output = True, input = test_sql)
    assert act.clean_stdout == act.clean_expected_stdout
