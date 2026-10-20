#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/71ebb207628cd4f2e33c7e43c5fc6e1d7b58a957
TITLE:       Use simpler method to skip indices that should not receive updates from new records, remove unneded any more RDB$FORMAT from RDB$INDICES
DESCRIPTION:
NOTES:
    [21.10.2026] pzotov
    Test scenario originally was found by zcode.ai. Simplified for better readability.
    Discussed with Vlad et al, letters since 16.10.2026 00:34.
    Confirmed regression on 6.0.0.2389-6b5f150, 6.0.0.2211 (latest snapshot which had no this problem: 6.0.0.2199).
    Checked on 6.0.0.2405-e71116c.
"""
from pathlib import Path
import subprocess

import pytest
from firebird.qa import *

init_sql = """
    create table t72 (id int, nm varchar(20));
    commit;
    insert into t72 values (1,'aaa');
    commit;
    create index t72_id on t72(id);
    create index t72_nm  on t72(nm);
    commit;
"""
db = db_factory(init = init_sql)

substitutions = []

act = python_act('db', substitutions = substitutions)

#---------------------------
def show_cursor_output(msg, cur, debug_show_plan = 0):
    print(f'\n\n{msg}:', cur.statement.sql,  f'\n{cur.statement.detailed_plan}' if debug_show_plan else '')
    print('Result:', cur.fetchall())
#---------------------------

@pytest.mark.ai
@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    qry_map = {
       300 : ('cur3. Indexed `T72_ID`'   ,   'select /* trace_me con3.1 */ id from t72 where id = 2'),
       350 : ('cur3. Natural'            ,   'select /* trace_me con3.2 */ id from t72 where id+0 = 2'),
       600 : ('cur6. Indexed `T72_NM`'   ,   "select /* trace_me con6.1 */ id from t72 where nm = 'ccc'"),
       650 : ('cur6. Natural'            ,   "select /* trace_me con6.2 */ count(*) from t72 where nm || '' = 'ccc'"),
       700 : ('cur7. Indexed `T72_ID`'   ,   "select /* trace_me con7.1 */ id from t72 where id = 2"),
       710 : ('cur7. Indexed `T72_NM`'   ,   "select /* trace_me con7.2 */ id from t72 where nm = 'ccc'"),
       750 : ('cur7. All ID, list'       ,   'select /* trace_me con7.3 */ list(id) from t72'),
    }

    with act.db.connect() as con1:
        cur1 = con1.cursor()
        cur1.execute("alter index t72_id inactive") # open => irt_commit  ai: att-7, tra-11

        with act.db.connect() as con2:
            cur2 = con2.cursor()
            cur2.execute("insert into t72 values (2,'bbb')") # ai: att-8
            con2.commit()
            with act.db.connect() as con3: #ai: att-9
                cur3 = con3.cursor()

                # befor: PLAN ("PUBLIC"."T72" INDEX ("PUBLIC"."T72_ID"))
                # after: PLAN ("PUBLIC"."T72" INDEX ("PUBLIC"."T72_ID"))
                cur3.execute( qry_map[300][1] )
                show_cursor_output( qry_map[300][0], cur3)

                cur3.execute( qry_map[350][1] )
                show_cursor_output( qry_map[350][0], cur3)

                con1.rollback() # ai: att-7   ***   r o l l b a c k  *** `alter index t72_id inactive`
                con3.rollback() # ai: att-9
            # < con3

            with act.db.connect() as con4: #ai: att-10
                cur4 = con4.cursor()
                cur4.execute("alter index t72_nm inactive") # open => irt_commit  ai: att-10, tra-18

                with act.db.connect() as con5: # ai: att-11
                    cur5 = con5.cursor()
                    cur5.execute("insert into t72 values (3,'ccc')") # ai: att-11, tra-20
                    con5.commit()

                    with act.db.connect() as con6: # ai: att-12
                        cur6 = con6.cursor()

                        # before: PLAN ("PUBLIC"."T72" INDEX ("PUBLIC"."T72_NM")) // 1 records fetched ; 3 fetch(es); IR: "PUBLIC"."T72" = 1
                        # after:  PLAN ("PUBLIC"."T72" INDEX ("PUBLIC"."T72_NM")) // 0 records fetched ; 2 fetch(es).
                        cur6.execute(qry_map[600][1]) # <<<<<<<<<<<< MISMATCH HERE <<<<<<<<<<<<
                        show_cursor_output(qry_map[600][0], cur6)

                        cur6.execute(qry_map[650][1])
                        show_cursor_output(qry_map[650][0], cur6)

                        con4.rollback() # ai: att-10  ***  r o l b a c k  *** `alter index t72_nm inactive`
                        con6.rollback() # ai: att-12
            #< con4

            with act.db.connect() as con7: #ai: att-13
                cur7 = con7.cursor()

                # before: PLAN ("PUBLIC"."T72" INDEX ("PUBLIC"."T72_ID")) // 1 records fetched ; 3 fetch(es)
                # after:  PLAN ("PUBLIC"."T72" INDEX ("PUBLIC"."T72_ID")) // 1 records fetched ; 3 fetch(es)
                cur7.execute(qry_map[700][1])
                show_cursor_output(qry_map[700][0], cur7)

                # befor: PLAN ("PUBLIC"."T72" INDEX ("PUBLIC"."T72_NM")) // 1 records fetched ; 3 fetch(es); IR: "PUBLIC"."T72" = 1
                # after: PLAN ("PUBLIC"."T72" INDEX ("PUBLIC"."T72_NM")) // 0 records fetched ; 2 fetch(es).
                cur7.execute(qry_map[710][1]) # <<<<<<<<<<<< MISMATCH HERE <<<<<<<<<<<<
                show_cursor_output(qry_map[710][0], cur7)

                cur7.execute(qry_map[750][1])
                show_cursor_output(qry_map[750][0], cur7)
                con7.rollback()
        # < con2
    # < con1

    act.expected_stdout = f"""
        {qry_map[300][0]}: {qry_map[300][1]}
        Result: [(2,)]

        {qry_map[350][0]}: {qry_map[350][1]}
        Result: [(2,)]

        {qry_map[600][0]}: {qry_map[600][1]}
        Result: [(3,)]

        {qry_map[650][0]}: {qry_map[650][1]}
        Result: [(1,)]

        {qry_map[700][0]}: {qry_map[700][1]}
        Result: [(2,)]

        {qry_map[710][0]}: {qry_map[710][1]}
        Result: [(3,)]

        {qry_map[750][0]}: {qry_map[750][1]}
        Result: [('1,2,3',)]
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()

