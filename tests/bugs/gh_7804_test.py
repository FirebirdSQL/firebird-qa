#coding:utf-8

"""
ID:          issue-7804
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7804
TITLE:       The partial index is not involved when filtering conditions through OR.
DESCRIPTION:
    https://github.com/FirebirdSQL/firebird/commit/8ad2531e1125e5346eeb98c7879baa73cf79cc84 // FB 5.x
    https://github.com/FirebirdSQL/firebird/commit/09ae711a4ec486046bf9dcb764d3f9babff124d9 // FB 6.x
    We put several queries into the array and check for each of them:
        * detailed execution plan;
        * number of natural and indexed reads.
          Number of NR must always be 0.
          Number of IR should increase in proportion to the number of 'OR' terms in the WHERE expression.
NOTES:
    [01.11.2023] pzotov
        0. ::: NB ::: TEST IS LIKELY TO BE SUPPLEMENTED WITH OTHER CASES.
        1. Explained plan must be displayed with preserved indents, see call to func replace_leading().
        2. Statistics is gathered using con.info.get_table_access_stats() method.
           One need to remember that values are cumulative, so we have make two 'snapshots',
           before and after query execution, and then calculate difference between them.

        Checked on 6.0.0.101.

    [16.12.2023] pzotov
        Adjusted output to recent changes in FB, currently only for FB 5.x.
        See:
            https://github.com/FirebirdSQL/firebird/commit/ae427762d5a3e740b69c7239acb9e2383bc9ca83
            More realistic cardinality adjustments for unmatchable booleans, this should also fix #7904: FB5 bad plan for query

        Output for FB 6.x will be changed later (letter from dimitr, 16.12.2023 10:32)
"""
import pytest
from firebird.qa import *

init_script = """
    recreate table test(x smallint);
    commit;

    insert into test(x) select nullif( mod( row_number()over(),10 ), 0 ) from rdb$types, rdb$types rows 10000;
    commit;

    create index test_x_asc on test(x) where x = 1 or x = 2 or x = 3 or x is null;
    create descending index test_x_dec on test(x) where x = 4 or x = 5 or x = 6 or x is null;
    commit;
"""

db = db_factory(init=init_script)

act = python_act('db')

#----------------------------------------------------------

def replace_leading(source, char="#"):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#----------------------------------------------------------

@pytest.mark.version('>=5.0')
def test_1(act: Action, capsys):
    
    q_list = (
        'select * from test where x = 1'
       ,'select * from test where x = 3 or x = 2'
       ,'select * from test where x = 2 or x = 3 or x = 1'
       ,'select * from test where x = 2 or x is null or x = 3 or x = 1'
       ,'select * from test where x = 5'
       ,'select * from test where x = 6 or x = 5'
       ,'select * from test where x = 5 or x = 4 or x = 6'
       ,'select * from test where x = 6 or x is null or x = 4 or x = 5'
    )

    with act.db.connect() as con:
        cur = con.cursor()
        cur.execute("select rdb$relation_id from rdb$relations where rdb$relation_name = upper('test')")
        test_rel_id = None
        for r in cur:
            test_rel_id = r[0]
        assert test_rel_id

        result_map = {}

        for x in q_list:
            with cur.prepare(x) as ps:
                tabstat1 = [ p for p in con.info.get_table_access_stats() if p.table_id == test_rel_id ]
                cur.execute(x)
                for r in cur:
                    pass
                tabstat2 = [ p for p in con.info.get_table_access_stats() if p.table_id == test_rel_id ]

                if tabstat1:
                    result_map[x, ps.detailed_plan] = \
                        (
                           (tabstat2[0].sequential if tabstat2[0].sequential else 0) - (tabstat1[0].sequential if tabstat1[0].sequential else 0)
                          ,(tabstat2[0].indexed if tabstat2[0].indexed else 0) - (tabstat1[0].indexed if tabstat1[0].indexed else 0)
                        )
                else:
                    result_map[x, ps.detailed_plan] = \
                        (
                           tabstat2[0].sequential if tabstat2[0].sequential else 0
                          ,tabstat2[0].indexed if tabstat2[0].indexed else 0
                        )

    for k,v in result_map.items():
        print('Query:', k[0])
        print( '\n'.join([replace_leading(s) for s in k[1].split('\n')]) ) # explained plan, with preserving indents by replacing leading spaces with '#'
        print('NR:', v[0])
        print('IR:', v[1])
        print('')

    #--------------------------------------------------------------------

    expected_fb5x = f"""
        Query: {q_list[0]}
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap
        ################-> Index "TEST_X_ASC" Range Scan (full match)
        NR: 0
        IR: 1000

        Query: select * from test where x = 3 or x = 2
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap Or
        ################-> Bitmap
        ####################-> Index "TEST_X_ASC" Range Scan (full match)
        ################-> Bitmap
        ####################-> Index "TEST_X_ASC" Range Scan (full match)
        NR: 0
        IR: 2000

        Query: select * from test where x = 2 or x = 3 or x = 1
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap Or
        ################-> Bitmap Or
        ####################-> Bitmap
        ########################-> Index "TEST_X_ASC" Range Scan (full match)
        ####################-> Bitmap
        ########################-> Index "TEST_X_ASC" Range Scan (full match)
        ################-> Bitmap
        ####################-> Index "TEST_X_ASC" Range Scan (full match)
        NR: 0
        IR: 3000

        Query: select * from test where x = 2 or x is null or x = 3 or x = 1
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap Or
        ################-> Bitmap Or
        ####################-> Bitmap Or
        ########################-> Bitmap
        ############################-> Index "TEST_X_ASC" Range Scan (full match)
        ########################-> Bitmap
        ############################-> Index "TEST_X_ASC" Range Scan (full match)
        ####################-> Bitmap
        ########################-> Index "TEST_X_ASC" Range Scan (full match)
        ################-> Bitmap
        ####################-> Index "TEST_X_ASC" Range Scan (full match)
        NR: 0
        IR: 4000

        Query: select * from test where x = 5
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap
        ################-> Index "TEST_X_DEC" Range Scan (full match)
        NR: 0
        IR: 1000

        Query: select * from test where x = 6 or x = 5
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap Or
        ################-> Bitmap
        ####################-> Index "TEST_X_DEC" Range Scan (full match)
        ################-> Bitmap
        ####################-> Index "TEST_X_DEC" Range Scan (full match)
        NR: 0
        IR: 2000

        Query: select * from test where x = 5 or x = 4 or x = 6
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap Or
        ################-> Bitmap Or
        ####################-> Bitmap
        ########################-> Index "TEST_X_DEC" Range Scan (full match)
        ####################-> Bitmap
        ########################-> Index "TEST_X_DEC" Range Scan (full match)
        ################-> Bitmap
        ####################-> Index "TEST_X_DEC" Range Scan (full match)
        NR: 0
        IR: 3000

        Query: select * from test where x = 6 or x is null or x = 4 or x = 5
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap Or
        ################-> Bitmap Or
        ####################-> Bitmap Or
        ########################-> Bitmap
        ############################-> Index "TEST_X_DEC" Range Scan (full match)
        ########################-> Bitmap
        ############################-> Index "TEST_X_DEC" Range Scan (full match)
        ####################-> Bitmap
        ########################-> Index "TEST_X_DEC" Range Scan (full match)
        ################-> Bitmap
        ####################-> Index "TEST_X_DEC" Range Scan (full match)
        NR: 0
        IR: 4000
    """


    expected_fb6x = f"""
        Query: {q_list[0]}
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap
        ################-> Index "TEST_X_ASC" Range Scan (full match)
        NR: 0
        IR: 1000

        Query: {q_list[1]}
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap Or
        ################-> Bitmap
        ####################-> Index "TEST_X_ASC" Range Scan (full match)
        ################-> Bitmap
        ####################-> Index "TEST_X_ASC" Range Scan (full match)
        NR: 0
        IR: 2000
        
        Query: {q_list[2]}
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap Or
        ################-> Bitmap Or
        ####################-> Bitmap
        ########################-> Index "TEST_X_ASC" Range Scan (full match)
        ####################-> Bitmap
        ########################-> Index "TEST_X_ASC" Range Scan (full match)
        ################-> Bitmap
        ####################-> Index "TEST_X_ASC" Range Scan (full match)
        NR: 0
        IR: 3000
        
        Query: {q_list[3]}
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap
        ################-> Index "TEST_X_ASC" Full Scan
        NR: 0
        IR: 4000
        
        Query: {q_list[4]}
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap
        ################-> Index "TEST_X_DEC" Range Scan (full match)
        NR: 0
        IR: 1000
        
        Query: {q_list[5]}
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap Or
        ################-> Bitmap
        ####################-> Index "TEST_X_DEC" Range Scan (full match)
        ################-> Bitmap
        ####################-> Index "TEST_X_DEC" Range Scan (full match)
        NR: 0
        IR: 2000
        
        Query: {q_list[6]}
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap Or
        ################-> Bitmap Or
        ####################-> Bitmap
        ########################-> Index "TEST_X_DEC" Range Scan (full match)
        ####################-> Bitmap
        ########################-> Index "TEST_X_DEC" Range Scan (full match)
        ################-> Bitmap
        ####################-> Index "TEST_X_DEC" Range Scan (full match)
        NR: 0
        IR: 3000
        
        Query: {q_list[7]}
        Select Expression
        ####-> Filter
        ########-> Table "TEST" Access By ID
        ############-> Bitmap
        ################-> Index "TEST_X_DEC" Full Scan
        NR: 0
        IR: 4000
    """

    act.expected_stdout = expected_fb5x if act.is_version('<6') else expected_fb6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
