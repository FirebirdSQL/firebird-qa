#coding:utf-8

"""
ID:          n/a
ISSUE:       https://groups.google.com/g/firebird-devel/c/8vlKSNckyuw/m/BTSkzb6wAQAJ
TITLE:       LTT with index. Crash when DDL + DML are in the same Tx and 'COMMIT' presents between 'DROP INDEX' and 'DROP TABLE'.
DESCRIPTION:
    Test uses two issues that were detected for LTT (second of them which uses EDS was found occasionally 07.06.2026).
    Both of them cause FB crash on 'commit' statements which are marked as "[ ! ]".
NOTES:
    [07.06.2026] pzotov
    Discission:
        https://groups.google.com/g/firebird-devel/c/8vlKSNckyuw/m/BTSkzb6wAQAJ
    Fixed in:
        https://github.com/FirebirdSQL/firebird/commit/08aa760318e64c211d443351b0e453976d214577
    Confirmed bug on 6.0.0.1996-263e09.
    Checked on 6.0.0.1999-c8bc46b.
"""

import pytest
from firebird.qa import *

COMPLETED_MSG = 'Ok'

db = db_factory()
act = python_act('db')

@pytest.mark.version('>=6.0')
def test_1(act: Action):

    test_sql_lst = (
        f"""
            set bail on;
            set heading off;
            set autoterm on;
            set autoddl off;
            commit;

            recreate LOCAL TEMPORARY table test(f01 int) on commit DELETE rows;
            commit;
            insert into test(f01) select i from generate_series(1, 1000) as s(i);

            create index test_idx on test(f01);
            drop index test_idx;

            commit; ----------------------- [ ! ]

            drop table test;
            commit;

            select '{COMPLETED_MSG}' as msg from rdb$database;
        """
        ,
        f"""
            set bail on;
            set heading off;
            set autoterm on;
            create procedure sp_make_ltt_using_es as
                declare i smallint;
                declare v_commit_action varchar(8);
            begin
                execute statement 'create LOCAL TEMPORARY table test_ltt_eds (f01 int) on commit delete rows';
                execute statement 'create index test_ltt_eds_f01 on test_ltt_eds(f01)';
                execute statement 'drop index test_ltt_eds_f01';
            end;
            commit;

            execute block as
            begin
                execute statement ('execute procedure sp_make_ltt_using_es')
                on external 'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME')
                as user '{act.db.user}' password '{act.db.password}'
                ;
            end
            ;
            commit; --------------------------- [ ! ]
            select '{COMPLETED_MSG}' as msg from rdb$database;
        """
    )

    for sql_i in test_sql_lst:
        act.expected_stdout = f"""
            {COMPLETED_MSG}
        """
        act.isql(input = sql_i, combine_output = True)
        assert act.clean_stdout == act.clean_expected_stdout
        act.reset()
