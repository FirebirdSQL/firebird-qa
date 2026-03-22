#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8948
TITLE:       Natural scan may occur for a query that has EXISTS and several joins in the inner subquery.
DESCRIPTION:
NOTES:
    Original title: 'Firebird 5.0.4 snapshot (build 1784) performance issue'.
    Explained plan before fix did not use index on t_outer as 'o2' (inside subquery).
    Thanks to dimitr for suggestions about test implementation details.

    Confirmeg bug on 6.0.0.1835-048e7c1; 5.0.4.1783-efed600.
    Checked on 6.0.0.1835-28db67e; 5.0.4.1785-8157ec5.
"""

from firebird.driver import DatabaseError
import pytest
from firebird.qa import *

db = db_factory()
act = isql_act('db')

#-----------------------------------------------------------
def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped
#-----------------------------------------------------------

@pytest.mark.version('>=5.0.4')
def test_1(act: Action, capsys):

    init_script = """
        set bail on;
        recreate table t_outer(
            id int primary key using index t_out_pk
        );
        recreate table t_inner(
            id int primary key using index t_inn_pk
           ,obj_id int references t_outer(id) using index t_inn_fk
           ,mezo_id int
        );
        create index t_inn_mezo on t_inner(mezo_id);

        -- Add some data, athough explained plans difference can be seen - currently - without this:
        insert into t_outer select row_number()over() from rdb$types rows 100;
        insert into t_inner(id, obj_id) select i, 1 + mod(i,100) from (select row_number()over() i from rdb$types, rdb$types rows 10000);
        update t_inner set mezo_id = mod(id, 13);
        commit;

        set statistics index t_out_pk;
        set statistics index t_inn_pk;
        set statistics index t_inn_fk;
        set statistics index t_inn_mezo;
        commit;
    """

    act.isql(switches = ['-q'], input = init_script, combine_output = True)
    assert act.clean_stdout == '', 'Init script FAILED: {act.clean_stdout=}'
    act.reset()

    qry_map = {
        1000 :
        """
            select distinct 1
            from t_outer o
            where exists (
                select 1
                from t_inner ia
                join t_inner ib on ib.id = ia.mezo_id
                join t_outer o2 on o2.id = ib.obj_id
                where ia.obj_id = o.id
            )
        """
    }


    with act.db.connect() as con:
        cur = con.cursor()
        for k, v in qry_map.items():
            ps, rs = None, None
            try:
                ps = cur.prepare(v)
                print(v)
                # Print explained plan with padding eash line by dots in order to see indentations:
                print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )
                print('')
            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)
            finally:
                if rs:
                    rs.close() # <<< EXPLICITLY CLOSING CURSOR RESULTS
                if ps:
                    ps.free()
        


    expected_stdout_5x = f"""
        {qry_map[1000]}
        Sub-query
        ....-> Nested Loop Join (inner)
        ........-> Filter
        ............-> Table "T_INNER" as "IA" Access By ID
        ................-> Bitmap
        ....................-> Index "T_INN_FK" Range Scan (full match)
        ........-> Filter
        ............-> Table "T_INNER" as "IB" Access By ID
        ................-> Bitmap
        ....................-> Index "T_INN_PK" Unique Scan
        ........-> Filter
        ............-> Table "T_OUTER" as "O2" Access By ID
        ................-> Bitmap
        ....................-> Index "T_OUT_PK" Unique Scan
        Select Expression
        ....-> Unique Sort (record length: 36, key length: 8)
        ........-> Filter
        ............-> Table "T_OUTER" as "O" Full Scan
    """

    expected_stdout_6x = f"""
        {qry_map[1000]}
        Select Expression
        ....-> Nested Loop Join (semi)
        ........-> Unique Sort (record length: 36, key length: 8)
        ............-> Table "PUBLIC"."T_OUTER" as "O" Full Scan
        ........-> Nested Loop Join (inner)
        ............-> Filter
        ................-> Table "PUBLIC"."T_INNER" as "IA" Access By ID
        ....................-> Bitmap
        ........................-> Index "PUBLIC"."T_INN_FK" Range Scan (full match)
        ............-> Filter
        ................-> Table "PUBLIC"."T_INNER" as "IB" Access By ID
        ....................-> Bitmap
        ........................-> Index "PUBLIC"."T_INN_PK" Unique Scan
        ............-> Filter
        ................-> Table "PUBLIC"."T_OUTER" as "O2" Access By ID
        ....................-> Bitmap
        ........................-> Index "PUBLIC"."T_OUT_PK" Unique Scan
    """

    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout

