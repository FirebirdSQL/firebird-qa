#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/263e09d6c0ab49d0f7dde7b2e1fe7486843e055e
TITLE:       Allow to mix DDL and DML in Created LLT in the same transaction
DESCRIPTION:
    Test makes two checks (see scripts in 'test_sql_lst') with verifying that DDL and DML can be mixed:
    1) in "static" SQL;
    2) in dynamic code (using EXECUTE STATEMENT mechanism, see procedure 'sp_run_ddl_and_dml_via_es').
NOTES:
    [07.06.2026] pzotov
    Weird bug exists that can cause exception with 'Integer overflow' message, see:
    https://groups.google.com/g/firebird-devel/c/_TD0JCw9Fdc/m/e5eNGTAWAgAJ
    The test likely will likely be supplemented after fix this oddity.
    
    Confirmed problems on 6.0.0.1995-e588f9e.
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
            set keep_tran on;
            set autoddl off;
            commit;
            create LOCAL TEMPORARY table ltt_test(f01 int) on commit delete rows;
            insert into ltt_test(f01) select i from generate_series(1, 1000) as s(i);
            update ltt_test set f01 = -f01 where mod(f01,3) <= 2;
            alter table ltt_test alter f01 type int128;
            update ltt_test set f01 = 170141183460469231731687303715884105727 where mod(f01,3) = 0;
            drop table ltt_test;

            create LOCAL TEMPORARY table ltt_test(f01 int) on commit preserve rows;
            insert into ltt_test(f01) select i from generate_series(1, 1000) as s(i);
            update ltt_test set f01 = -f01 where mod(f01,3) <= 2;
            alter table ltt_test alter f01 type int128;
            update ltt_test set f01 = 170141183460469231731687303715884105727 where mod(f01,3) = 0;
            drop table ltt_test;

            select '{COMPLETED_MSG}' as msg from rdb$database;
        """
        ,
        f"""
            -- https://groups.google.com/g/firebird-devel/c/_TD0JCw9Fdc/m/e5eNGTAWAgAJ
            set bail on;
            set heading off;
            set autoterm on;
            set keep_tran on;
            set autoddl off;
            commit;
            create procedure sp_run_ddl_and_dml_via_es(a_table_name varchar(31), a_index_name varchar(31)) as
                declare i smallint;
                declare n smallint;
                declare v_commit_action varchar(8);
            begin
                i = 1;
                n = 2;
                while (i <= n) do
                begin
                    v_commit_action = iif(i = 1, 'DELETE', 'PRESERVE');
                    -- execute statement 'create LOCAL TEMPORARY table ' || a_table_name || '(f01 int) on commit ' || v_commit_action || ' rows';
                    -- execute statement 'create GLOBAL TEMPORARY table ' || a_table_name || '(f01 int) on commit ' || v_commit_action || ' rows';
                    execute statement 'create table ' || a_table_name || '(f01 int)';
                    execute statement 'insert into ' || a_table_name || '(f01) select i from generate_series(1, 1000) as s(i)';

                    -- ###################
                    -- ###   N O T E   ###
                    -- ###################
                    -- execute statement 'update /* ACHTUNG */ ' || a_table_name || ' set f01 = -f01 where mod(f01,3) <= 2';
                    execute statement 'update /* ACHTUNG: ' || v_commit_action || ' rows */ ' || a_table_name || ' set f01 = -f01 where mod(f01,3) <= 2';

                    execute statement 'alter table ' || a_table_name || ' alter f01 type int128';
                    execute statement ('update ' || a_table_name || ' set f01 = ? where mod(f01,3) = ?') (170141183460469231731687303715884105727, 0);
                    execute statement 'drop table ' || a_table_name;
                    i = i + 1;
                end
            end;
            commit;

            execute block as
            begin
                execute procedure sp_run_ddl_and_dml_via_es('test_es_1', 'test_es_1_idx');
            end
            ;
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
