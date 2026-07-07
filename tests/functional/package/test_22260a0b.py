#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/22260a0bc6c6313d8aaba5b1cafa934d059d6592
TITLE:       Fixed drop of attachment-level GTT reported in devel
DESCRIPTION:
NOTES:
    [07.07.2026] pzotov
    Initial discussion:
    https://groups.google.com/g/firebird-devel/c/azqX6VgM59k/m/oOkRbGaLAQAJ
    Confirmed crash on 6.0.0.2062-0-f9055bf
    Checked on 6.0.0.2067-16f511e.
"""

import pytest
from firebird.qa import *

COMPLETED_MSG = 'Ok'

db = db_factory()
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):

    # all lines marked as "[ 1 ]" ... "[ 4 ]" are mandatory to reproduce bug.
    test_sql = f"""
        set bail on;
        set autoddl off;
        set autoterm on;
        set keep_tran on;
        set heading off;
        create or alter package pg_temp_tab as
        begin
            procedure sp_fill;
        end
        ;

        recreate package body pg_temp_tab as
        begin
            temporary table pg_priv_table(id int, f01 boolean) on commit
                preserve -------------------------------------------- [ 1 ]
                -- delete
                rows
                index pg_priv_table_idx(id) ------------------------- [ 2 ]
            ;
            procedure sp_fill as
            begin
                insert into pg_priv_table(id, f01) values(1, false);
            end
        end
        ;

        execute procedure pg_temp_tab.sp_fill; --------------------- [ 3 ]
        commit; ---------------------------------------------------- [ 4 ]
        alter package pg_temp_tab as
        begin
            -- nope --
        end
        ;
        select '{COMPLETED_MSG}' from rdb$database;
    """

    act.expected_stdout = f"""
        {COMPLETED_MSG}
    """
    act.isql(switches = ['-q'], input = test_sql, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
