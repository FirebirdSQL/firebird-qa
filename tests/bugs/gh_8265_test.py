#coding:utf-8

"""
ID:          issue-8265
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8265
TITLE:       Nested IN/EXISTS subqueries should not be converted into semi-joins if the outer context is a sub-query which wasn't unnested
DESCRIPTION:
NOTES:
    [26.09.2024] pzotov
    0. ::: NB ::: This test probably will be reimplemented later, see note by dimitr in the ticket:
       "In the future this heuristics should be replaced with a cost-based approach between hash and nested loop semi-join"
    1. Parameter 'SubQueryConversion' currently presents only in FB 5.x and _NOT_ in FB 6.x.
       Because of that, testing version are limited only for 5.0.2. FB 6.x currently is NOT tested.
    2. Custom driver config objects are created here, one with SubQueryConversion = true and second with false.
    3. First example of this test is also used in tests/functional/tabloid/test_aae2ae32.py
    
    Confirmed problem on 5.0.2.1516-fe6ba50 (23.09.2024).
    Checked on 5.0.2.1516-92316F0 (25.09.2024).
"""

import pytest
from firebird.qa import *
from firebird.driver import driver_config, connect, DatabaseError

init_script = """
    create table test1(id int not null);
    create table test2(id int not null, pid int not null);
    create table test3(id int not null, pid int not null, name varchar(30) not null);
    commit;

    insert into test1(id) select row_number()over()-1 from rdb$types rows 10;
    insert into test2(id, pid) select row_number()over()-1, mod(row_number()over()-1, 10) from rdb$types rows 100;
    insert into test3(id, pid, name) select row_number()over()-1, mod(row_number()over()-1, 100), 'QWEABCRTY' from rdb$types, rdb$types rows 1000;
    commit;
"""

db = db_factory(init=init_script)

act = python_act('db', substitutions = [('record length: \\d+', 'record length')])

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

@pytest.mark.version('>=5.0.2,<6')
def test_1(act: Action, capsys):

    test_query_lst = [
        """
            -- Example 1: both sub-queries can (and should) be unnested.
            select count(*) from test1 q1_a
            where
                q1_a.id in (
                    select q1_b.pid from test2 q1_b
                    where
                        q1_b.id in (
                            select q1_c.pid from test3 q1_c
                            where q1_c.name like '%ABC%'
                        )
                )
        """,
        """
            -- Example 2: inner sub-query cannot be unnested due to OR condition present, but the outer sub-query can
            select count(*) from test1 q2_a
            where
                q2_a.id in (
                    select q2_b.pid from test2 q2_b
                    where
                        1=1 or q2_b.id in (
                            select q2_c.pid from test3 q2_c
                            where q2_c.name like '%ABC%'
                        )
                )
        """,
        """
            -- Example-3: outer sub-query cannot be unnested due to OR condition present, so the inner sub-query should NOT be unnested too.
            select count(*) from test1 q3_a
            where
                1=1 or q3_a.id in (
                    select q3_b.pid from test2 q3_b
                    where q3_b.id in (
                        select id from test3 q3_c
                        where q3_c.name like '%ABC%'
                    )
                )
        """,
        """
            -- Example-4: both sub-queries can NOT be unnested due to OR conditions present.
            select count(*) from test1 q4_a
            where
                1=1 or q4_a.id in (
                    select id from test2 q4_b
                    where
                        1=1 or q4_b.id in (
                            select id from test3 q4_c
                            where q4_c.name like '%ABC%'
                        )
                    )
        """
    ]


    for sq_conv in ('true','false',):
        srv_cfg = driver_config.register_server(name = f'srv_cfg_aae2ae32_{sq_conv}', config = '')
        db_cfg_name = f'db_cfg_aae2ae32_{sq_conv}'
        db_cfg_object = driver_config.register_database(name = db_cfg_name)
        db_cfg_object.server.value = srv_cfg.name
        db_cfg_object.database.value = str(act.db.db_path)
        db_cfg_object.config.value = f"""
            SubQueryConversion = {sq_conv}
        """

        with connect(db_cfg_name, user = act.db.user, password = act.db.password) as con:
            for idx, test_sql in enumerate(test_query_lst):
                try:
                    cur = con.cursor()
                    cur.execute("select g.rdb$config_name, g.rdb$config_value from rdb$database r left join rdb$config g on g.rdb$config_name = 'SubQueryConversion'")
                    for r in cur:
                        print(r[0],r[1])

                    ps = cur.prepare(test_sql)

                    print(f'\nExample {idx+1}')
                    # Print explained plan with padding eash line by dots in order to see indentations:
                    print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )

                    # Print data:
                    for r in cur.execute(ps):
                        print(r[0])
                except DatabaseError as e:
                    print(e.__str__())
                    print(e.gds_codes)

    act.expected_stdout = f"""
        SubQueryConversion true
        Example 1
        Select Expression
        ....-> Aggregate
        ........-> Filter
        ............-> Hash Join (semi)
        ................-> Table "TEST1" as "Q1_A" Full Scan
        ................-> Record Buffer (record length)
        ....................-> Filter
        ........................-> Hash Join (semi)
        ............................-> Table "TEST2" as "Q1_B" Full Scan
        ............................-> Record Buffer (record length)
        ................................-> Filter
        ....................................-> Table "TEST3" as "Q1_C" Full Scan
        10

        SubQueryConversion true
        Example 2
        Sub-query
        ....-> Filter
        ........-> Filter
        ............-> Table "TEST3" as "Q2_C" Full Scan
        Select Expression
        ....-> Aggregate
        ........-> Filter
        ............-> Hash Join (semi)
        ................-> Table "TEST1" as "Q2_A" Full Scan
        ................-> Record Buffer (record length)
        ....................-> Filter
        ........................-> Table "TEST2" as "Q2_B" Full Scan
        10

        SubQueryConversion true
        Example 3
        Sub-query
        ....-> Filter
        ........-> Filter
        ............-> Table "TEST3" as "Q3_C" Full Scan
        Sub-query
        ....-> Filter
        ........-> Filter
        ............-> Table "TEST2" as "Q3_B" Full Scan
        Select Expression
        ....-> Aggregate
        ........-> Filter
        ............-> Table "TEST1" as "Q3_A" Full Scan
        10

        SubQueryConversion true
        Example 4
        Sub-query
        ....-> Filter
        ........-> Filter
        ............-> Table "TEST3" as "Q4_C" Full Scan
        Sub-query
        ....-> Filter
        ........-> Filter
        ............-> Table "TEST2" as "Q4_B" Full Scan
        Select Expression
        ....-> Aggregate
        ........-> Filter
        ............-> Table "TEST1" as "Q4_A" Full Scan
        10

        
        SubQueryConversion false
        Example 1
        Sub-query
        ....-> Filter
        ........-> Filter
        ............-> Table "TEST3" as "Q1_C" Full Scan
        Sub-query
        ....-> Filter
        ........-> Filter
        ............-> Table "TEST2" as "Q1_B" Full Scan
        Select Expression
        ....-> Aggregate
        ........-> Filter
        ............-> Table "TEST1" as "Q1_A" Full Scan
        10

        SubQueryConversion false
        Example 2
        Sub-query
        ....-> Filter
        ........-> Filter
        ............-> Table "TEST3" as "Q2_C" Full Scan
        Sub-query
        ....-> Filter
        ........-> Filter
        ............-> Table "TEST2" as "Q2_B" Full Scan
        Select Expression
        ....-> Aggregate
        ........-> Filter
        ............-> Table "TEST1" as "Q2_A" Full Scan
        10

        SubQueryConversion false
        Example 3
        Sub-query
        ....-> Filter
        ........-> Filter
        ............-> Table "TEST3" as "Q3_C" Full Scan
        Sub-query
        ....-> Filter
        ........-> Filter
        ............-> Table "TEST2" as "Q3_B" Full Scan
        Select Expression
        ....-> Aggregate
        ........-> Filter
        ............-> Table "TEST1" as "Q3_A" Full Scan
        10

        SubQueryConversion false
        Example 4
        Sub-query
        ....-> Filter
        ........-> Filter
        ............-> Table "TEST3" as "Q4_C" Full Scan
        Sub-query
        ....-> Filter
        ........-> Filter
        ............-> Table "TEST2" as "Q4_B" Full Scan
        Select Expression
        ....-> Aggregate
        ........-> Filter
        ............-> Table "TEST1" as "Q4_A" Full Scan
        10

    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
