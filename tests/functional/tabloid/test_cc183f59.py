#coding:utf-8

"""
ID:          functional.tabloid.test_cc183f59
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/cc183f599ee09233d6da294893f651de0ab76136
TITLE:       Add key info to the merge join plan output
DESCRIPTION:
NOTES:
    MERGE JOIN will be chosen by optimizer when several conditions are met:
    * data sources are joined by INNER join;
    * data sources are ORDERED, BUT *NOT* via GROUP BY (because optimizer tends to think about grouped data
      that its cardinality *much* less than cardinality of source and it causes to decide using hash join instead).
      This was explained by dimitr privately, letter: 24-sep-2024 16:30.
    * number of conflicts in the hash table must be above 1009 * 1000 = 1009000.
      Experimental shows that minimal threshold for switching from HJ to MJ is 1009883 rows.
      This value must NOT depend on machine but can have limited dependency on page_size
      (see letter from dimitr, 24-sep-2024 19:09).
    * No ticket has been created for this test.
    Checked on 6.0.0.467.

    [06.11.2026]
    Increased number of rows for 4x otherwise optimizer chooses HASH JOIN instead, see 'N_MIN_ROWS_FOR_MERGE_JOIN'.
    This (changed) behaviour started since
    https://github.com/FirebirdSQL/firebird/commit/86daeaf3d74c5b207a3562c853cb1c0148e8eacd
    (letter from dimitr, 06.11.2026 15:30).
    NOTE: test duration increased up to ~22".
    Checked on 6.0.0.2447-77d8185.
"""

import re
import time
from firebird.driver import DatabaseError

import pytest
from firebird.qa import *

#########################
N_MIN_ROWS_FOR_MERGE_JOIN = 4039532
#########################

db = db_factory(page_size = 8192)

substitutions =  [  ('[ \t]+', ' ')
                   ,('keys: \\d+, total key length: \\d+', 'keys, total key length')
                   ,('record length: \\d+, key length: \\d+', 'record length, key length')
                 ]

act = python_act('db', substitutions = substitutions)

#-----------------------------------------------------------

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    init_sql = f"""
        create local temporary table test1(id int not null) on commit preserve rows ^
        create local temporary table test2(id int not null) on commit preserve rows ^
        insert into test1(id) select i from generate_series(0,{N_MIN_ROWS_FOR_MERGE_JOIN }) as s(i) ^
        insert into test2(id) select i from generate_series(0,{N_MIN_ROWS_FOR_MERGE_JOIN}) as s(i) ^
        commit ^
    """
    test_sql = """
        select a.id as a_id, b.id as b_id
        from (
            select id from test1 order by id
        ) a
        join 
        (
            select id from test2 b order by id
        ) b
        on a.id = b.id
    """

    with act.db.connect() as con:
        for x in [s.strip() for s in init_sql.split('^') if s.strip()]:
            if x.lower() == 'commit'.lower():
                con.commit()
            else:
                con.execute_immediate(x)

        cur = con.cursor()
        ps = None
        try:
            ps = cur.prepare(test_sql)
            print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )
        except DatabaseError as e:
            print( e.__str__() )
            print(e.gds_codes)
        finally:
            if ps:
                ps.free()

    act.expected_stdout = """
        Select Expression
        ....-> Filter
        ........-> Merge Join (inner) (keys, total key length)
        ............-> Sort (record length, key length)
        ................-> Sort (record length, key length)
        ....................-> Table "PUBLIC"."TEST1" as "A" "PUBLIC"."TEST1" Full Scan
        ............-> Sort (record length, key length)
        ................-> Sort (record length, key length)
        ....................-> Table "PUBLIC"."TEST2" as "B" "B" Full Scan
    """

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
