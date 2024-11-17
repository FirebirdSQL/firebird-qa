#coding:utf-8

"""
ID:          optimizer.sort-by-index-18
TITLE:       ORDER BY ASC using index (single) and WHERE clause
DESCRIPTION:
    WHERE X = 1 ORDER BY Y
    Index for both X and Y should be used when available.
FBTEST:      functional.arno.optimizer.opt_sort_by_index_18
NOTES:
    [17.11.2024] pzotov
    Re-implemented after https://github.com/FirebirdSQL/firebird/commit/26e64e9c08f635d55ac7a111469498b3f0c7fe81
    ( Cost-based decision between ORDER and SORT plans (#8316) ).
    Execution plan was replaced with explained. Plans are splitted for versions up to 5.x and 6.x+.
    Discussed with dimitr, letters 16.11.2024.

    Checked on 6.0.0.532; 5.0.2.1567; 4.0.6.3168; 3.0.13.33794.
"""

import pytest
from firebird.qa import *

init_sql = """
    recreate table table_53 (
      id1 integer,
      id2 integer
    );

    set term ^ ;
    create procedure pr_filltable_53
    as
        declare k integer;
        declare i integer;
    begin
        k = 1;
        while (k <= 50) do
        begin
            i = (k / 10) * 10;
            insert into table_53 (id1, id2) values (:i, :k - :i);
            k = k + 1;
        end
        insert into table_53 (id1, id2) values (0, null);
        insert into table_53 (id1, id2) values (null, 0);
        insert into table_53 (id1, id2) values (null, null);
    end
    ^
    set term ;^
    commit;

    execute procedure pr_filltable_53;
    commit;

    create asc index i_table_53_id1_asc on table_53 (id1);
    create desc index i_table_53_id1_desc on table_53 (id1);
    create asc index i_table_53_id2_asc on table_53 (id2);
    create desc index i_table_53_id2_desc on table_53 (id2);
    commit;
"""

db = db_factory(init = init_sql)

act = python_act('db', substitutions = [(r'record length: \d+, key length: \d+', 'record length: NN, key length: MM')])

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

@pytest.mark.version('>=3')
def test_1(act: Action, capsys):

    # opt_clause = '' if act.is_version('<5') else 'optimize for first rows' if act.is_version('<6') else ''
    opt_clause = ''

    test_sql = f"""
        select
            t53.id2,
            t53.id1
        from table_53 t53
        where
            t53.id1 = 30
        order by
            t53.id2 asc
        {opt_clause}
    """

    with act.db.connect() as con:
        cur = con.cursor()
        ps = None
        try:
            ps = cur.prepare(test_sql)

            # Print explained plan with padding eash line by dots in order to see indentations:
            # print(test_sql)
            print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )
            print('')
        except DatabaseError as e:
            print(e.__str__())
            print(e.gds_codes)
        finally:
            if ps:
                ps.free()

    expected_stdout_5x = """
        Select Expression
        ....-> Filter
        ........-> Table "TABLE_53" as "T53" Access By ID
        ............-> Index "I_TABLE_53_ID2_ASC" Full Scan
        ................-> Bitmap
        ....................-> Index "I_TABLE_53_ID1_ASC" Range Scan (full match)
    """

    expected_stdout_6x = """
        Select Expression
        ....-> Sort (record length: NN, key length: MM)
        ........-> Filter
        ............-> Table "TABLE_53" as "T53" Access By ID
        ................-> Bitmap
        ....................-> Index "I_TABLE_53_ID1_ASC" Range Scan (full match)
    """

    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
