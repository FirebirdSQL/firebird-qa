#coding:utf-8

"""
ID:          issue-5228
ISSUE:       5228
TITLE:       View/subselect with "union" does not use computed index
DESCRIPTION:
    Difference was found between 2.5.5.26916 and 2.5.5.26933 snapshots.
    Also, on 3.0.0.32052 there was no NR.
    Current QA suit cann not be used for check such ancient versions.
JIRA:        CORE-4937
NOTES:
    [23.06.2026]
    Refactored: removed (extremely) old code that determines number of NR and IR via MON$ tables.
    We can obtain such values just by querying con.info.get_table_access_stats().
    We do *not* check and compare execution plans because they can change in the future and for this test
    it is enough only to check that NR-value in all cases is zero.

    Checked on 6.0.0.2023; 5.0.5.1837; 4.0.8.3286; 3.0.15.33867
"""

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError

#################
ROWS_TO_ADD = 200
#################

init_script = f"""
    create sequence g;

    recreate view v_unioned as select 1 id from rdb$database;
    recreate table test1 (id int not null primary key, tms timestamp default current_timestamp);
    recreate table test2 (id int not null primary key, tms timestamp default current_timestamp);

    alter table test1 add occurred int computed by (case when tms < current_timestamp then 1 else 0 end);

    alter table test2 add occurred int;

    recreate view v_unioned as select * from test1 union select * from test2;
    commit;

    insert into test1(id, tms)
    select n.m * t.i, dateadd( n.m * t.i minute to cast('now' as timestamp) )
    from (
        select row_number()over() i from rdb$types rows {ROWS_TO_ADD}
    ) t
    cross join(select -1 m from rdb$database union all select 1 from rdb$database) n
    ;
    insert into test2(id, tms) select id, tms
    from test1
    ;
    update test2 set occurred = iif(tms < current_timestamp,1,0);
    commit;

    create index t1_computed on test1 computed by (case when tms < current_timestamp then 1 else 0 end);
    create index t2_regular on test2(occurred);
    commit;

"""
db = db_factory(init = init_script)
act = python_act('db')

@pytest.mark.version('>=3')
def test_1(act: Action, capsys):
    q_list = (
       'select count(*) from (select * from test1 union select * from test2) where occurred = 1',
       'select count(*) from v_unioned where occurred = 1',
    )

    with act.db.connect() as con:
        cur = con.cursor()
        cur.execute("select rdb$relation_id from rdb$relations where rdb$relation_name in (?, ?)", ('test1'.upper(), 'test2'.upper()) )
        test_id_lst = []
        for r in cur:
            test_id_lst.append(r[0])
        assert test_id_lst

        for x in q_list:
            ps, rs =  None, None
            seq = idx = 0
            try:
                ps = cur.prepare(x)
                tabstat1 = [ p for p in con.info.get_table_access_stats() if p.table_id in test_id_lst ]
                for p in tabstat1:
                    seq -= p.sequential if p.sequential else 0
                    idx -= p.indexed if p.indexed else 0
                rs = cur.execute(ps)
                for r in rs:
                    pass
                tabstat2 = [ p for p in con.info.get_table_access_stats() if p.table_id in test_id_lst ]
                for p in tabstat2:
                    seq += p.sequential if p.sequential else 0
                    idx += p.indexed if p.indexed else 0
                print(x)
                print(f'{seq=}, {idx=}')
            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)
            finally:
                if rs:
                    rs.close() # <<< EXPLICITLY CLOSING CURSOR RESULTS
                if ps:
                    ps.free()

    act.expected_stdout = f"""
        {q_list[0]}
        seq=0, idx={2*ROWS_TO_ADD}

        {q_list[1]}
        seq=0, idx={2*ROWS_TO_ADD}
     """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout

