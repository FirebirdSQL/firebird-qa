#coding:utf-8

"""
ID:          issue-7863
ISSUE:       7863
TITLE:       Non-correlated sub-query is evaluated multiple times if it is based on a VIEW rathe than on appropriate derived table.
DESCRIPTION:
NOTES:
    [18.01.2025] pzotov
    Resultset of cursor that executes using instance of selectable PreparedStatement must be stored
    in some variable in order to have ability close it EXPLICITLY (before PS will be freed).
    Otherwise access violation raises during Python GC and pytest hangs at final point (does not return control to OS).
    This occurs at least for: Python 3.11.2 / pytest: 7.4.4 / firebird.driver: 1.10.6 / Firebird.Qa: 0.19.3
    The reason of that was explained by Vlad, 26.10.24 17:42 ("oddities when use instances of selective statements").
   
    Confirmed bug on 6.0.0.222
    Checked on 6.0.0.223, 5.0.1.1322.
"""

from pathlib import Path

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError

init_sql = """
    create view v_test_nr as select 1 i from rdb$fields rows 50;
    create view v_test_ir1 as select 1 i from rdb$fields where rdb$field_name > '' rows 50;
    create view v_test_ir2 as select 1 i from rdb$fields where rdb$field_name > '' order by rdb$field_name rows 50;
     
    create table test(id int);
    insert into test(id) select row_number()over() from rdb$types rows 100;
    commit;
"""
db = db_factory(init = init_sql)

act = python_act('db')

@pytest.mark.version('>=5.0.1')
def test_1(act: Action, capsys):

    t_map = { 'rdb$fields' : -1, }

    query1 = """
        select /* case-2 */ count(*) as cnt_via_view from test where (select i from v_test_nr rows 1) >= 0;
    """

    query2 = """
        select /* case-3b */ count(*) as cnt_via_view from test where (select i from v_test_ir2 rows 1) >= 0;
    """

    query3 = """
        select /* case-3a */ count(*) as cnt_via_view from test where (select i from v_test_ir1 rows 1) >= 0;
    """
    q_map = {query1 : '', query2 : '', query3 : ''}
    
    with act.db.connect() as con:
        cur = con.cursor()
        for k in t_map.keys():
            cur.execute(f"select rdb$relation_id from rdb$relations where rdb$relation_name = upper('{k}')")
            test_rel_id = None
            for r in cur:
                test_rel_id = r[0]
            assert test_rel_id, f"Could not find ID for relation '{k}'. Check its name!"
            t_map[ k ] = test_rel_id

        result_map = {}

        for qry_txt in q_map.keys():
            ps, rs = None, None
            try:
                ps = cur.prepare(qry_txt)
                q_map[qry_txt] = ps.detailed_plan
                for tab_nm,tab_id in t_map.items():
                    tabstat1 = [ p for p in con.info.get_table_access_stats() if p.table_id == tab_id ]
            
                    # ::: NB ::: 'ps' returns data, i.e. this is SELECTABLE expression.
                    # We have to store result of cur.execute(<psInstance>) in order to
                    # close it explicitly.
                    # Otherwise AV can occur during Python garbage collection and this
                    # causes pytest to hang on its final point.
                    # Explained by hvlad, email 26.10.24 17:42
                    rs = cur.execute(ps)
                    for r in rs:
                        pass
                    tabstat2 = [ p for p in con.info.get_table_access_stats() if p.table_id == tab_id ]

                    result_map[qry_txt, tab_nm] = \
                        (
                           tabstat2[0].sequential if tabstat2[0].sequential else 0
                          ,tabstat2[0].indexed if tabstat2[0].indexed else 0
                        )
                    if tabstat1:
                        seq, idx = result_map[qry_txt, tab_nm]
                        seq -= (tabstat1[0].sequential if tabstat1[0].sequential else 0)
                        idx -= (tabstat1[0].indexed if tabstat1[0].indexed else 0)
                        result_map[qry_txt, tab_nm] = (seq, idx)
            except DatabaseError as e:
                print( e.__str__() )
                print(e.gds_codes)
            finally:
                if rs:
                    rs.close() # <<< EXPLICITLY CLOSING CURSOR RESULTS
                if ps:
                    ps.free()

        for k,v in result_map.items():
            print(k[0]) # query
            print(f'seq={v[0]}, idx={v[1]}')
            print('')

    act.expected_stdout = f"""
        {query1}
        seq=1, idx=0

        {query2}
        seq=0, idx=1

        {query3}
        seq=0, idx=1
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
