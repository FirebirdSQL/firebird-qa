#coding:utf-8

"""
ID:          n/a
ISSUE:       
TITLE:       DECLARED TEMPORARY TABLE. Check access from local subroitines
DESCRIPTION:
NOTES:
    [27.07.2026] pzotov
    Currently example from doc/sql.extensions/README.declared_local_temporary_tables.md is used (with minor chages).
    Checked 6.0.0.2092-3fa7269.
"""
import locale
import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' '), ('LOCAL_PROC_RESULT [0-9a-fA-F]{16}', 'LOCAL_PROC_RESULT')]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    test_script = """
        SET BAIL ON; -- [ 1 ]
        set list on;
        set autoterm on;
        create domain dm_rdb_key char(8) character set octets;
        commit;
        execute block returns (
             local_proc_result dm_rdb_key
            ,local_func_result integer
            ,id_sum_result integer
        ) as
            declare local temporary table t (
                id integer
            );

            declare procedure p_add(v integer) returns(local_proc_result dm_rdb_key) as
            begin
                insert into t values (:v) returning rdb$db_key into local_proc_result;
                suspend;
            end

            declare function f_count returns integer
            as
                declare variable ret integer;
            begin
                select count(*) from t into ret;
                return ret;
            end
        begin
            insert into t values (1);
            execute procedure p_add(2) returning_values local_proc_result;

            local_func_result = f_count();
            select sum(id) from t into id_sum_result;
            suspend;
        end;
    """

    act.expected_stdout = """
        LOCAL_PROC_RESULT 00F8000002000000
        LOCAL_FUNC_RESULT 2
        ID_SUM_RESULT 3
    """
    act.isql(switches=['-q'], input = test_script, combine_output = True, io_enc = locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
