#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/9045
TITLE:       Fix calling reload twice for package constants and improve hash calculation
DESCRIPTION:
    Source description:
    https://groups.google.com/g/firebird-devel/c/xIxhL_QAjEg/m/yMjlPxnuAQAJ
    ("Package constants. Weird message "HY000 / Statement format outdated" can raise")
    See also:
    https://github.com/FirebirdSQL/firebird/pull/9022
NOTES:
    Fixed by commit: e588f9ea47b36d88c3020cde0e31b9b129c394ac
    Confirmed problem on 6.0.0.1992-00d5916
    Checked on 6.0.0.1995-e588f9e.
"""

import pytest
from firebird.qa import *

COMPLETED_MSG = 'Ok'

db = db_factory()
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):

    test_sql = f"""
        set bail on;
        set list on;
        set autoterm on;
        create package pg_test as
        begin
            constant s_head smallint = 1;
            procedure sp_test returns(sp_outcome smallint);
            function fn_test returns smallint;
        end
        ;
        recreate package body pg_test as
        begin
            constant s_body smallint = -1; ------------------------------------------- [ 1 ]
            procedure sp_test returns(sp_outcome smallint) as
            begin
                sp_outcome = s_head;
                suspend;
            end

            function fn_test returns smallint as
            begin
                return 1;
            end
        end
        ;
        commit;
        connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}'; --- [ 2 ]
        set bail OFF;

        select sp_outcome as result_1 from pg_test.sp_test;

        select pg_test.fn_test() as result_2  from rdb$database;

        select pg_test.fn_test() as result_3 from pg_test.sp_test rows 1;
    """

    act.expected_stdout = f"""
        RESULT_1                        1
        RESULT_2                        1
        RESULT_3                        1
    """
    act.isql(switches = ['-q'], input = test_sql, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()

    ##########################################################################

    # from https://github.com/FirebirdSQL/firebird/pull/9022
    test_sql = f"""
        set bail on;
        set list on;
        set autoterm on;
        create package pg_9022
        as
        begin
            procedure sp_test(i int) returns (o int); -- public procedure
            constant header_const integer = 10;
        end
        ;
        create package body pg_9022 as
        begin
            constant cp2 integer = 15;
            constant cp3 integer = 30;
            procedure sp_test(i int) returns (o int) as
            begin
                o = pg_9022.header_const + pg_9022.cp2;
                suspend;
            end
        end
        ;
        commit;

        select pg_9022.header_const as pg_9022_hdr_const from rdb$database;
        select p.o as pg_9022_sp_out from pg_9022.sp_test(0) p;
        commit;
    """

    act.expected_stdout = f"""
        PG_9022_HDR_CONST 10
        PG_9022_SP_OUT 25
    """
    act.isql(switches = ['-q'], input = test_sql, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
