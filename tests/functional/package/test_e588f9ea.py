#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/9045
TITLE:       Fix calling reload twice for package constants and improve hash calculation
DESCRIPTION:
    Source description:
    https://groups.google.com/g/firebird-devel/c/xIxhL_QAjEg/m/yMjlPxnuAQAJ
    ("Package constants. Weird message "HY000 / Statement format outdated" can raise")
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
