z`#coding:utf-8

"""
ID:          issue-3811
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/3811
TITLE:       Inefficient optimization (regression)
DESCRIPTION:
JIRA:        CORE-3450
FBTEST:      bugs.core_3450
NOTES:
    [13.04.2026] pzotov
    Refactored: execution plan is shown in explained form.
    Adjusted output in 6.x to current (letter from dimitr, 13.04.2026 0855).
    Checked on 6.0.0.1891; 5.0.4.1808; 4.0.7.3269; 3.0.14.33855.
"""

import pytest
from firebird.qa import *

init_script = """
    set bail on;
    create or alter procedure sp_add_data as begin end;
    recreate table test_1 (f1 int, f2 int, f3 int);
    recreate table test_2 (f1 int, f2 int);
    recreate table test_3 (f1 int);
    commit;
    set term ^;
    create or alter procedure sp_for_join returns (f1 int) as
    begin
        f1=1;
        suspend;
    end
    ^

    create or alter procedure sp_add_data as
      declare i int;
      declare t1_lim int = 1000;
      declare t2_lim int = 100;
      declare t3_lim int = 10;
    begin
        i=0;
        while (i<t1_lim) do begin
            i=i+1;
            insert into test_1 values (:i, 1, 3);
        end

        i=0;
        while (i<t2_lim) do begin
            i=i+1;
            insert into test_2 values (:i, 2);
        end

        i=0;
        while (i<t3_lim) do begin
            i=i+1;
            insert into test_3 values (3);
        end
    end
    ^
    set term ;^
    commit;

    execute procedure sp_add_data;
    commit;

    create index test_1_f1 on test_1(f1);
    create index test_1_f2 on test_1(f2);
    create index test_2_f1 on test_2(f1);
    create index test_2_f2 on test_2(f2);
    create index test_3_f1 on test_3(f1);
    commit;

    set statistics index test_1_f1;
    set statistics index test_1_f2;
    set statistics index test_2_f1;
    set statistics index test_2_f2;
    set statistics index test_3_f1;
    commit;
"""

db = db_factory(init = init_script)

act = python_act('db')

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):
    test_sql = """
        select t2.f1
        from test_2 t2
        join test_1 t1 on t1.f1=t2.f1
        join sp_for_join p1 on p1.f1=t1.f2
        join test_3 t3 on t3.f1=t1.f3
        where t2.f2=2;
    """

    with act.db.connect() as con:
        cur = con.cursor()
        ps, rs = None, None
        try:
            cur = con.cursor()
            ps = cur.prepare(test_sql)

            # Print explained plan with padding eash line by dots in order to see indentations:
            print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )

            # ::: NB ::: 'ps' returns data, i.e. this is SELECTABLE expression.
            # We have to store result of cur.execute(<psInstance>) in order to
            # close it explicitly.
            # Otherwise AV can occur during Python garbage collection and this
            # causes pytest to hang on its final point.
            # Explained by hvlad, email 26.10.24 17:42
            #rs = cur.execute(ps)
            #for r in rs:
            #    print(r[0], r[1], r[2])
        except DatabaseError as e:
            print(e.__str__())
            print(e.gds_codes)
        finally:
            if rs:
                rs.close() # <<< EXPLICITLY CLOSING CURSOR RESULTS
            if ps:
                ps.free()
    

    expected_stdout_4x = """
        Select Expression
        ....-> Nested Loop Join (inner)
        ........-> Nested Loop Join (inner)
        ............-> Procedure "SP_FOR_JOIN" as "P1" Scan
        ............-> Filter
        ................-> Table "TEST_1" as "T1" Access By ID
        ....................-> Bitmap
        ........................-> Index "TEST_1_F2" Range Scan (full match)
        ........-> Filter
        ............-> Table "TEST_2" as "T2" Access By ID
        ................-> Bitmap
        ....................-> Index "TEST_2_F1" Range Scan (full match)
        ........-> Filter
        ............-> Table "TEST_3" as "T3" Access By ID
        ................-> Bitmap
        ....................-> Index "TEST_3_F1" Range Scan (full match)
    """

    expected_stdout_5x = """
        Select Expression
        ....-> Nested Loop Join (inner)
        ........-> Procedure "SP_FOR_JOIN" as "P1" Scan
        ........-> Filter
        ............-> Table "TEST_1" as "T1" Access By ID
        ................-> Bitmap
        ....................-> Index "TEST_1_F2" Range Scan (full match)
        ........-> Filter
        ............-> Table "TEST_2" as "T2" Access By ID
        ................-> Bitmap
        ....................-> Index "TEST_2_F1" Range Scan (full match)
        ........-> Filter
        ............-> Table "TEST_3" as "T3" Access By ID
        ................-> Bitmap
        ....................-> Index "TEST_3_F1" Range Scan (full match)
    """

    expected_stdout_6x = """
        Select Expression
        ....-> Nested Loop Join (inner)
        ........-> Procedure "PUBLIC"."SP_FOR_JOIN" as "P1" Scan
        ........-> Filter
        ............-> Table "PUBLIC"."TEST_1" as "T1" Access By ID
        ................-> Bitmap
        ....................-> Index "PUBLIC"."TEST_1_F2" Range Scan (full match)
        ........-> Filter
        ............-> Table "PUBLIC"."TEST_2" as "T2" Access By ID
        ................-> Bitmap
        ....................-> Index "PUBLIC"."TEST_2_F1" Range Scan (full match)
        ........-> Filter
        ............-> Table "PUBLIC"."TEST_3" as "T3" Access By ID
        ................-> Bitmap
        ....................-> Index "PUBLIC"."TEST_3_F1" Range Scan (full match)
    """

    act.expected_stdout = expected_stdout_4x if act.is_version('<5') else expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
