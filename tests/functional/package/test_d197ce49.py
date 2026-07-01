#coding:utf-8

"""
ID:          n/a
ISSUE:       https://groups.google.com/g/firebird-devel/c/uPpRhaAKT0M/m/uczwM_cVAwAJ
TITLE:       Package constants. FB crashes if package body constant is queried
DESCRIPTION:
NOTES:
    [01.07.2026] pzotov
    See also: https://github.com/FirebirdSQL/firebird/pull/9065
    Fixed by commit: d197ce494de2826df6ef1a6f9c0dae220bd5c960
    Confirmed problem on 6.0.0.2028-348f7aa.
    Checked on 6.0.0.2050-09246e5.
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
        set autoddl off;
        set keep_tran on;
        commit;
        recreate package pg_test as
        begin
            procedure sp_test() returns(o smallint);
        end
        ;
        recreate package body pg_test as
        begin
            constant PG_BODY_CONST smallint = -10;
            procedure sp_test() returns(o smallint) as
            begin
                o = pg_body_const;
                suspend;
            end
        end
        ;
        commit;

        select p.o as get_pkg_const from pg_test.sp_test as p rows 1; -- segfault
    """

    act.expected_stdout = f"""
        GET_PKG_CONST -10
    """
    act.isql(switches = ['-q'], input = test_sql, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
