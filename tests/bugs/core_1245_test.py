#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/1669
TITLE:       Incorrect column values with outer joins and views
DESCRIPTION:
NOTES:
    [20.02.2026] pzotov
        Re-implemented: FULL JOIN execution plan has changed since 19.02.2026 6.0.0.1458, commit:
        "6a76c1da Better index usage in full outer joins...".  This changed the order of rows in resultset.
        The fix is simple: we can add 'ORDER BY' to the query but this must not change execution plan
        (i.e. optimizer still has to use FULL JOIN in this case! Discussed with dimitr, 20.02.2026 1345).
        Because of this, explained plan is shown for additional check and it must contain 'Full Outer Join'.
        Min-version increased to 5.0 (no changes expected in FB 3.x/4.x related to FULL JOIN).
        Checked on 6.0.0.1461-5e98812; 5.0.4.1767-52823f5.
    [04.06.2026] pzotov
        Replaced RDB$DATABASE with regular singular-row table 't0' because test failed on FB 6.x since
        commit bb280120 (6.0.0.1959; 2026.05.21 05:41:14) when rbdb$relation_id ceased to be used as storage
        for last created relation ID.
        Checked on 6.0.0.1992; 5.0.5.1826.
"""

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError

init_script = """
    create table t0 (rel_id smallint); -- type exactly same as domain rdb$relation_id
    create table t1 (n int);
    create table t2 (n int);

    create view v_fj_data (n1, n2, n3) as
    select t1.n, t2.n, 3
    from t1
    full join t2 on t1.n = t2.n
    ;

    insert into t0(rel_id) values (128);

    insert into t1 values (1);
    insert into t1 values (2);
    insert into t2 values (2);
"""

db = db_factory(init=init_script)

substitutions = [('[ \t]+', ' '), ('(record|key)\\s+length(:)?\\s+\\d+', 'record/key length: NNN')]
act = python_act('db', substitutions = substitutions)

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

@pytest.mark.version('>=5')
def test_1(act: Action, capsys):
    query_map = {
        1000 : (
                    f"""
                        select r.rel_id, v.rdb$db_key as v_db_key, v.*
                        from t0 as r
                        full outer join v_fj_data as v on (1 = 0)
                        order by r.rel_id nulls last, v_db_key nulls last -- <<< added 20.02.2026
                    """
                   ,''
               )
    }

    with act.db.connect(charset = 'utf8') as con:
        cur = con.cursor()
        for q_idx, q_tuple in query_map.items():
            test_sql, qry_comment = q_tuple[:2]
            ps, rs = None, None
            try:
                print(q_idx)
                print(test_sql)
                print(qry_comment)
                ps = cur.prepare(test_sql)
                print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )
                rs = cur.execute(ps)
                cur_cols = cur.description
                for r in cur:
                    for i in range(0,len(cur_cols)):
                        if isinstance(r[i], bytes):
                            col_data = r[i].hex() # to make value RDB$DB_KEY as it is printed in ISQL
                        else:
                            col_data = r[i]
                        print( cur_cols[i][0], ':', col_data )
            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)
            finally:
                if rs:
                    rs.close()
                if ps:
                    ps.free()

    expected_stdout_5x = f"""
        1000
        {query_map[1000][0]}
        {query_map[1000][1]}
        Select Expression
        ....-> Sort (record/key length: NNN, record/key length: NNN)
        ........-> Full Outer Join
        ............-> Nested Loop Join (outer)
        ................-> Full Outer Join
        ....................-> Nested Loop Join (outer)
        ........................-> Table "T2" as "V T2" Full Scan
        ........................-> Filter
        ............................-> Table "T1" as "V T1" Full Scan
        ....................-> Nested Loop Join (outer)
        ........................-> Table "T1" as "V T1" Full Scan
        ........................-> Filter
        ............................-> Table "T2" as "V T2" Full Scan
        ................-> Filter
        ....................-> Table "T0" as "R" Full Scan
        ............-> Nested Loop Join (outer)
        ................-> Table "T0" as "R" Full Scan
        ................-> Full Outer Join
        ....................-> Nested Loop Join (outer)
        ........................-> Table "T2" as "V T2" Full Scan
        ........................-> Filter
        ............................-> Table "T1" as "V T1" Full Scan
        ....................-> Nested Loop Join (outer)
        ........................-> Table "T1" as "V T1" Full Scan
        ........................-> Filter
        ............................-> Table "T2" as "V T2" Full Scan

        REL_ID : 128
        V_DB_KEY : None
        N1 : None
        N2 : None
        N3 : None

        REL_ID : None
        V_DB_KEY : 00000000000000008100000001000000
        N1 : 1
        N2 : None
        N3 : 3

        REL_ID : None
        V_DB_KEY : 82000000010000008100000002000000
        N1 : 2
        N2 : 2
        N3 : 3
    """

    expected_stdout_6x = f"""
        1000
        {query_map[1000][0]}
        {query_map[1000][1]}
        Select Expression
        ....-> Sort (record/key length: NNN, record/key length: NNN)
        ........-> Full Outer Join
        ............-> Nested Loop Join (outer)
        ................-> Table "PUBLIC"."T0" as "R" Full Scan
        ................-> Full Outer Join
        ....................-> Nested Loop Join (outer)
        ........................-> Table "PUBLIC"."T1" as "V" "PUBLIC"."T1" Full Scan
        ........................-> Filter
        ............................-> Table "PUBLIC"."T2" as "V" "PUBLIC"."T2" Full Scan
        ....................-> Nested Loop Join (outer)
        ........................-> Table "PUBLIC"."T2" as "V" "PUBLIC"."T2" Full Scan
        ........................-> Filter
        ............................-> Table "PUBLIC"."T1" as "V" "PUBLIC"."T1" Full Scan
        ............-> Nested Loop Join (outer)
        ................-> Full Outer Join
        ....................-> Nested Loop Join (outer)
        ........................-> Table "PUBLIC"."T1" as "V" "PUBLIC"."T1" Full Scan
        ........................-> Filter
        ............................-> Table "PUBLIC"."T2" as "V" "PUBLIC"."T2" Full Scan
        ....................-> Nested Loop Join (outer)
        ........................-> Table "PUBLIC"."T2" as "V" "PUBLIC"."T2" Full Scan
        ........................-> Filter
        ............................-> Table "PUBLIC"."T1" as "V" "PUBLIC"."T1" Full Scan
        ................-> Table "PUBLIC"."T0" as "R" Full Scan

        REL_ID : 128
        V_DB_KEY : None
        N1 : None
        N2 : None
        N3 : None

        REL_ID : None
        V_DB_KEY : 00000000000000008100000001000000
        N1 : 1
        N2 : None
        N3 : 3

        REL_ID : None
        V_DB_KEY : 82000000010000008100000002000000
        N1 : 2
        N2 : 2
        N3 : 3
    """

    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
