#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8628
TITLE:       Incorrect join order for JOIN LATERAL with UNION, aggregate or window function referencing the outer stream(s) via its select list
DESCRIPTION:
NOTES:
    [17.07.2025] pzotov
    SQL schema name (introduced since 6.0.0.834), single and double quotes are suppressed in the output.
    See $QA_HOME/README.substitutions.md or https://github.com/FirebirdSQL/firebird-qa/blob/master/README.substitutions.md
    Confirmed problem on 6.0.0.877, 5.0.3.1622
    Checked on 6.0.0.1020, 5.0.3.1683
    [07.11.2026] AI assistant
    Added queries 2 and 3: the same problem when the select list of the LATERAL derived
    table contains an aggregate or a window function instead of a union clause.
    Confirmed on a 6.0 development build: before the fix both queries produced an inverted
    join order and failed at run time with "no current record for fetch operation".
"""

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError

db = db_factory()

substitutions = [(r'record length: \d+', 'record length: NN')]
# QA_GLOBALS -- dict, is defined in qa/plugin.py, obtain settings
# from act.files_dir/'test_config.ini':
#
addi_subst_settings = QA_GLOBALS['schema_n_quotes_suppress']
addi_subst_tokens = addi_subst_settings['addi_subst']

for p in addi_subst_tokens.split(' '):
    substitutions.append( (p, '') )

act = python_act('db', substitutions = substitutions)

#-----------------------------------------------------------

@pytest.mark.version('>=5.0.3')
def test_1(act: Action, capsys):

    qry_list = (
        """
            select t.name
            from rdb$relations r
            cross join lateral (
                select r.rdb$relation_name as name from rdb$database
                union all
                select r.rdb$owner_name as name from rdb$database
            ) t
        """,
        """
            select t.cnt
            from rdb$relations r
            cross join lateral (
                select count(d.rdb$relation_id + r.rdb$relation_id) as cnt from rdb$database d
            ) t
        """,
        """
            select t.cnt
            from rdb$relations r
            cross join lateral (
                select count(d.rdb$relation_id + r.rdb$relation_id) over () as cnt from rdb$database d
            ) t
        """,
    )

    with act.db.connect() as con:
        cur = con.cursor()
        for test_sql in qry_list:
            ps, rs =  None, None
            try:
                cur = con.cursor()
                ps = cur.prepare(test_sql)
                print(test_sql)
                # Print explained plan with padding eash line by dots in order to see indentations:
                print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )

                # ::: NB ::: 'ps' returns data, i.e. this is SELECTABLE expression.
                # We have to store result of cur.execute(<psInstance>) in order to
                # close it explicitly.
                # Otherwise AV can occur during Python garbage collection and this
                # causes pytest to hang on its final point.
                # Explained by hvlad, email 26.10.24 17:42
                rs = cur.execute(ps)
                for r in rs:
                    pass
                print('Fetching completed.')
            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)
            finally:
                if rs:
                    rs.close() # <<< EXPLICITLY CLOSING CURSOR RESULTS
                if ps:
                    ps.free()

    act.expected_stdout = f"""
        {qry_list[0]}
        Select Expression
        ....-> Nested Loop Join (inner)
        ........-> Table RDB$RELATIONS as R Full Scan
        ........-> Union
        ............-> Table RDB$DATABASE as T RDB$DATABASE Full Scan
        ............-> Table RDB$DATABASE as T RDB$DATABASE Full Scan
        Fetching completed.
        {qry_list[1]}
        Select Expression
        ....-> Nested Loop Join (inner)
        ........-> Table RDB$RELATIONS as R Full Scan
        ........-> Aggregate
        ............-> Table RDB$DATABASE as T D Full Scan
        Fetching completed.
        {qry_list[2]}
        Select Expression
        ....-> Nested Loop Join (inner)
        ........-> Table RDB$RELATIONS as R Full Scan
        ........-> Window
        ............-> Window Partition
        ................-> Window Buffer
        ....................-> Record Buffer (record length: NN)
        ........................-> Table RDB$DATABASE as T D Full Scan
        Fetching completed.
    """

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
