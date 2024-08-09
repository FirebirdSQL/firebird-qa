#coding:utf-8

"""
ID:          issue-3218
ISSUE:       3218
TITLE:       Optimizer fails applying stream-local predicates before merging [CORE2832]
DESCRIPTION:
    We evaluate number of records in rdb$relation_fields for which corresponding rows in rdb$relations have ID < 10.
    This value ('cnt_chk') must be equal to the number of indexed reads for this table when we run test query ('chk_sql').
    Before fix number of indexed reads in rdb$relation_fields was equal to the TOTAL number of rows in this table.
FBTEST:      bugs.gh_3218
NOTES:
    [20.01.2024] pzotov
    Confirmed problem on 5.0.0.442: number of indexed reads was equal to the total count of records in rdb$relation_fields.
    Checked on 6.0.0.218, 5.0.1.1318.
"""

import pytest
from pathlib import Path
from firebird.qa import *

init_sql = """
    set term ^;
    create or alter procedure sp_get_relations returns(
        rdb$relation_id type of column rdb$relations.rdb$relation_id,
        rdb$relation_name type of column rdb$relations.rdb$relation_name
    ) as
    begin
        for
        select
            rdb$relation_id,
            rdb$relation_name
        from rdb$relations
        into
            rdb$relation_id,
            rdb$relation_name
        do
        begin
            suspend;
        end
    end
    ^
    set term ;^
    commit;
"""
db = db_factory(init = init_sql)

act = python_act('db')

#----------------------------------------------------------

def replace_leading(source, char="#"):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#----------------------------------------------------------

@pytest.mark.version('>=5.0')
def test_1(act: Action, capsys):
    with act.db.connect() as con:
        cur = con.cursor()
        cur.execute("select rdb$relation_id from rdb$relations where rdb$relation_name = upper('rdb$relation_fields')")
        rf_rel_id = None
        for r in cur:
            rf_rel_id = r[0]
        assert rf_rel_id

        cur.execute("select count(iif(r.rdb$relation_id < 10, 1, null)) cnt_chk, count(*) as cnt_all from rdb$relation_fields rf left join rdb$relations r on rf.rdb$relation_name = r.rdb$relation_name and r.rdb$relation_id < 10")

        cnt_chk, cnt_all = cur.fetchall()[0][:2]
        
        #------------------------------------------------------

        result_map = {}
        chk_sql = 'select 1 from sp_get_relations r join rdb$relation_fields f on f.rdb$relation_name = r.rdb$relation_name where r.rdb$relation_id < 10'
        with cur.prepare(chk_sql) as ps:
            cur.execute(chk_sql)
            tabstat1 = [ p for p in con.info.get_table_access_stats() if p.table_id == rf_rel_id ]
            cur.fetchall()
            tabstat2 = [ p for p in con.info.get_table_access_stats() if p.table_id == rf_rel_id ]
            print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) ) # explained plan, with preserving indents by replacing leading spaces with '#'

        idx_reads = (tabstat2[0].indexed if tabstat2[0].indexed else 0)
        if tabstat1:
            idx_reads -= (tabstat1[0].indexed if tabstat1[0].indexed else 0)

        print('Result:')
        if idx_reads == 0 or idx_reads > cnt_chk:
            print(f'POOR! Number of records in rdb$relation_fields: 1) to be filtered: {cnt_chk}, 2) total: {cnt_all}. Number of indexed_reads: {idx_reads}')
        else:
            print('Acceptable.')

    act.expected_stdout = """
        Select Expression
        ####-> Nested Loop Join (inner)
        ########-> Filter
        ############-> Procedure "SP_GET_RELATIONS" as "R" Scan
        ########-> Filter
        ############-> Table "RDB$RELATION_FIELDS" as "F" Access By ID
        ################-> Bitmap
        ####################-> Index "RDB$INDEX_4" Range Scan (full match)
        Result:
        Acceptable.
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
