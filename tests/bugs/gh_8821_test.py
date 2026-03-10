#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8821
TITLE:       REGRESSION: natural plan instead of primary/unique index
DESCRIPTION:
NOTES:
    Confirmeg regression on 6.0.0.1811-89ef46f; 5.0.4.1780-2040071.
    Checked on 6.0.0.1814-ab9cd28; 5.0.4.1782-2f348fa; 4.0.7.3245; 3.0.14.33838.
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

@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):

    init_script = """
        set bail on;
        create table test1(id int);
        create table test2(id int);
        set term ^;
        create procedure sp_get_id(a_id int) returns(o_id int) as
        begin
            o_id = a_id;
            suspend;
        end
        ^
        execute block as
            declare n int = 1000;
        begin
            while (n > 0) do
            begin
                insert into test2(id) values(:n);
                n = n - 1;
            end
        end
        ^
        set term ;^
        commit;
        insert into test1 select min(id) from test2;
        commit;
        create unique index test2_unq on test2(id);
        commit;
    """

    act.isql(switches = ['-q'], input = init_script, combine_output = True)
    assert act.clean_stdout == '', 'Init script FAILED: {act.clean_stdout=}'
    act.reset()

    qry_map = {
        1000 :
        """
            select 1 x
            from
                test1 m 
                inner join sp_get_id(m.id) p on 1 = 1
                inner join test2 d on d.id = p.o_id
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
        

    expected_stdout_4x = f"""
        {qry_map[1000]}
        Select Expression
        ....-> Nested Loop Join (inner)
        ........-> Filter
        ............-> Table "TEST1" as "M" Full Scan
        ........-> Nested Loop Join (inner)
        ............-> Procedure "SP_GET_ID" as "P" Scan
        ............-> Filter
        ................-> Table "TEST2" as "D" Access By ID
        ....................-> Bitmap
        ........................-> Index "TEST2_UNQ" Unique Scan
    """

    expected_stdout_5x = f"""
        {qry_map[1000]}
        Select Expression
        ....-> Filter (preliminary)
        ........-> Nested Loop Join (inner)
        ............-> Table "TEST1" as "M" Full Scan
        ............-> Procedure "SP_GET_ID" as "P" Scan
        ............-> Filter
        ................-> Table "TEST2" as "D" Access By ID
        ....................-> Bitmap
        ........................-> Index "TEST2_UNQ" Unique Scan
    """

    expected_stdout_6x = f"""
        {qry_map[1000]}
        Select Expression
        ....-> Filter (preliminary)
        ........-> Nested Loop Join (inner)
        ............-> Table "PUBLIC"."TEST1" as "M" Full Scan
        ............-> Procedure "PUBLIC"."SP_GET_ID" as "P" Scan
        ............-> Filter
        ................-> Table "PUBLIC"."TEST2" as "D" Access By ID
        ....................-> Bitmap
        ........................-> Index "PUBLIC"."TEST2_UNQ" Unique Scan
    """

    act.expected_stdout = expected_stdout_4x if act.is_version('<5') else expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout

