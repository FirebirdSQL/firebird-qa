#coding:utf-8

"""
ID:          issue-8946
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/8946
TITLE:       PERCENTILE_CONT and PERCENTILE_DISC functions
DESCRIPTION:
    The single test_1 contains two parts.
    Part 1 has two examples from the ticket.
    Part 2 is a regression check for a scalar sub-select in the WITHIN GROUP (ORDER BY ...)
    clause of PERCENTILE_CONT()/PERCENTILE_DISC(): such a statement in an ad-hoc query, in a
    windowed form and in a view used to fail with "context already in use (BLR error)" (or,
    for the view DDL, with "invalid request BLR at offset ...").
NOTES:
    [29.03.2026] pzotov
        Test uses DDL and data from employee DB but they have been extracted to .sql and stored in
        files/standard_sample_databases.zip (file: "sample-DB_-_firebird.sql").
        Default names of all constraints were replaced in order to easy find appropriate table.
        Checked on 6.0.0.1858-c0190d0.
    [11.05.2026] pzotov
        Adjusted output after #b5b5b0e (Fixed PERCENT_RANK computation (#8970)).
        Checked on 6.0.0.1910.
    [06.11.2026] AI assistant
        Added second part of the test. The value argument of a percentile aggregate is aliased from the first
        item of the WITHIN GROUP (ORDER BY ...) clause, and PercentileAggNode::dsqlCopy() passed
        only the order clause: the very same sub-select node was left in the copy, and genBlr()
        wrote its context twice into the BLR. Ad-hoc statements and views with such a statement
        used to fail at run time with "context already in use (BLR error)", and the view DDL was
        rejected at creation with "invalid request BLR at offset ...".
        Checked on 6.0.0.2447-a75c543.
    [07.11.2026] pzotov
        Refactored so that all queries are performed within single test function (see 'qry_map' items).
        Checked on 6.0.0.2454-28bc822.
"""

import pytest
import zipfile
from pathlib import Path
from firebird.qa import *
from firebird.driver import DatabaseError
import time

db = db_factory()
substitutions = []

act = python_act('db', substitutions = substitutions)
tmp_sql = temp_file('gh_8061.tmp.sql')

@pytest.mark.ai
@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_sql: Path, capsys):
    #------------------------------------------------------------------
    # PART 1: two examples of PERCENTILE_DISC()/PERCENTILE_CONT() usage
    # from the ticket.
    #------------------------------------------------------------------
    employee_data_sql = zipfile.Path(act.files_dir / 'standard_sample_databases.zip', at='sample-DB_-_firebird.sql')

    test_script = employee_data_sql.read_text(encoding = 'utf8')

    # added 07.11.2026:
    ###################
    test_script += """
        recreate table pct_t1 (id int, val numeric(15,4));
        recreate table pct_t2 (id int, t1id int, val int);
        create view v_pct_test as
        select
            percentile_cont(0.5)
            within group (
                             order by (
                                          select max(t2.val)
                                          from pct_t2 t2
                                          where t2.t1id = t1.id
                                      )
                         )
            as p_cont
            ,
            percentile_disc(0.5)
            within group (
                             order by (
                                          select max(t2.val)
                                          from pct_t2 t2
                                          where t2.t1id = t1.id
                                      )
                         )
            as p_disc
        from pct_t1 t1
        ;

        insert into pct_t1 values (1, 1.5);
        insert into pct_t1 values (2, 2.5);
        insert into pct_t1 values (3, 3.5);
        insert into pct_t2 values (1, 1, 10);
        insert into pct_t2 values (2, 2, 20);
        insert into pct_t2 values (3, 3, 30);
        commit;
    """

    tmp_sql.write_text(test_script, encoding = 'utf8')

    act.isql(switches = ['-q'], charset='utf8', input_file = tmp_sql, combine_output = True)
    if act.return_code == 0:
        pass
    else:
        # If retcode !=0 then we can print the whole output of failed gbak:
        print('Initial script failed, check output:')
        for line in act.clean_stdout.splitlines():
            print(line)
    act.reset()
    #----------------------------------------------------------------------
    qry_map = {
        1000 :
        (
            f"""
                select
                    dept_no
                    ,salary
                    ,cume_dist() over(partition by dept_no order by salary) as c_dist
                    ,percentile_disc(0.5) within group(order by salary) over(partition by dept_no) as median_disc
                from employee
                where dept_no < 600
                order by 1, 2
            """
            ,'Example of PERCENTILE_DISC() usage'
        )
        ,
        2000 :
        (
            f"""
                select
                    dept_no
                    ,salary
                    ,percent_rank() over(partition by dept_no order by salary) as prc_rank
                    ,percentile_cont(0.5) within group(order by salary) over(partition by dept_no) as median_cont
                from employee
                where dept_no < 600
                order by 1, 2
            """
            ,'Example of PERCENTILE_CONT() usage'
        )
        ,
        3100 :
        (
            f"""
                select
                    percentile_cont(0.5)
                    within group (
                                     order by (
                                                  select max(t2.val)
                                                  from pct_t2 t2
                                                  where t2.t1id = t1.id
                                              )
                                 ) as p_cont_correlated
                    ,
                    percentile_disc(0.5)
                    within group (
                                     order by (
                                                  select max(t2.val)
                                                  from pct_t2 t2
                                                  where t2.t1id = t1.id
                                              )
                                 ) as p_disc_correlated

                from pct_t1 t1
            """
            ,'correlated scalar sub-select in the WITHIN GROUP (ORDER BY ...) - query to the TABLE' 
        )
        ,
        3200 :
        (
            f"""
                select
                    percentile_cont(0.5)
                    within group (
                                     order by (
                                                  select avg(t2.val)
                                                  from pct_t2 t2
                                              )
                                 ) as p_cont_uncorrelated
                from pct_t1 t1
            """
            ,'uncorrelated sub-select' 
        )
        ,
        3300 :
        (
            f"""
                select
                    percentile_cont(0.5)
                    within group (
                                     order by (
                                                  select max(t2.val)
                                                  from pct_t2 t2
                                                  where t2.t1id = t1.id
                                              )
                                              DESC -- <<< NB <<<
                                 ) as p_cont_corr_desc_ord
                from pct_t1 t1
            """
            ,'percentile_cont: correlated scalar sub-select in the WITHIN GROUP (ORDER BY ...) DESCEND' 
        )
        ,
        3400 :
        (
            f"""
                select
                    percentile_cont(0.5) within group (order by t1.val) as p_cont_no_subquery
                    ,
                    percentile_disc(0.5) within group (order by t1.val) as p_disc_no_subquery
                from pct_t1 t1
            """
            ,'controls, no sub-select' 
        )
        ,
        3500 :
        (
            f"""
                select
                    t1.id as w1
                    ,
                    percentile_cont(0.5)
                    within group (
                                     order by (
                                                  select max(t2.val)
                                                  from pct_t2 t2
                                                  where t2.t1id = t1.id
                                              )
                                 ) over (partition by t1.id)
                    as p_cont_windowed
                from pct_t1 t1
                order by 1
            """
            ,'windowed form of WITHING GROUP(...)'
        )
        ,
        3600 :
        (
            f"""
                select v.*
                from v_pct_test v;
            """
            ,'correlated scalar sub-select in the WITHIN GROUP (ORDER BY ...) - query to the VIEW' 
        )
        ,
    }

    with act.db.connect() as con:
        cur = con.cursor()
        for q_idx, q_tuple in qry_map.items():
            test_sql, qry_comment = q_tuple[:2]
            ps, rs = None, None
            try:
                print(q_idx)
                print(test_sql)
                print(qry_comment)
                ps = cur.prepare(test_sql)
                #print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )
                rs = cur.execute(ps)
                cur_cols = cur.description
                for r in cur:
                    for i in range(0,len(cur_cols)):
                        print( cur_cols[i][0], ':', r[i] )
            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)
            finally:
                if rs:
                    rs.close()
                if ps:
                    ps.free()

    act.expected_stdout = f"""
        1000
        {qry_map[1000][0]}
        {qry_map[1000][1]}
        DEPT_NO : 000
        SALARY : 53793
        C_DIST : 0.5
        MEDIAN_DISC : 53793
        DEPT_NO : 000
        SALARY : 212850
        C_DIST : 1.0
        MEDIAN_DISC : 53793
        DEPT_NO : 100
        SALARY : 44000
        C_DIST : 0.5
        MEDIAN_DISC : 44000
        DEPT_NO : 100
        SALARY : 111262.5
        C_DIST : 1.0
        MEDIAN_DISC : 44000
        DEPT_NO : 110
        SALARY : 61637.81
        C_DIST : 0.5
        MEDIAN_DISC : 61637.81
        DEPT_NO : 110
        SALARY : 68805
        C_DIST : 1.0
        MEDIAN_DISC : 61637.81
        DEPT_NO : 115
        SALARY : 6000000
        C_DIST : 0.5
        MEDIAN_DISC : 6000000
        DEPT_NO : 115
        SALARY : 7480000
        C_DIST : 1.0
        MEDIAN_DISC : 6000000
        DEPT_NO : 120
        SALARY : 22935
        C_DIST : 0.3333333333333333
        MEDIAN_DISC : 33620.63
        DEPT_NO : 120
        SALARY : 33620.63
        C_DIST : 0.6666666666666666
        MEDIAN_DISC : 33620.63
        DEPT_NO : 120
        SALARY : 39224.06
        C_DIST : 1.0
        MEDIAN_DISC : 33620.63
        DEPT_NO : 121
        SALARY : 110000
        C_DIST : 1.0
        MEDIAN_DISC : 110000
        DEPT_NO : 123
        SALARY : 38500
        C_DIST : 1.0
        MEDIAN_DISC : 38500
        DEPT_NO : 125
        SALARY : 33000
        C_DIST : 1.0
        MEDIAN_DISC : 33000
        DEPT_NO : 130
        SALARY : 86292.94
        C_DIST : 0.5
        MEDIAN_DISC : 86292.94
        DEPT_NO : 130
        SALARY : 102750
        C_DIST : 1.0
        MEDIAN_DISC : 86292.94
        DEPT_NO : 140
        SALARY : 100914
        C_DIST : 1.0
        MEDIAN_DISC : 100914
        DEPT_NO : 180
        SALARY : 42742.5
        C_DIST : 0.5
        MEDIAN_DISC : 42742.5
        DEPT_NO : 180
        SALARY : 64635
        C_DIST : 1.0
        MEDIAN_DISC : 42742.5

        2000
        {qry_map[2000][0]}
        {qry_map[2000][1]}
        DEPT_NO : 000
        SALARY : 53793
        PRC_RANK : 0.0
        MEDIAN_CONT : 133321.5
        DEPT_NO : 000
        SALARY : 212850
        PRC_RANK : 1.0
        MEDIAN_CONT : 133321.5
        DEPT_NO : 100
        SALARY : 44000
        PRC_RANK : 0.0
        MEDIAN_CONT : 77631.25
        DEPT_NO : 100
        SALARY : 111262.5
        PRC_RANK : 1.0
        MEDIAN_CONT : 77631.25
        DEPT_NO : 110
        SALARY : 61637.81
        PRC_RANK : 0.0
        MEDIAN_CONT : 65221.405
        DEPT_NO : 110
        SALARY : 68805
        PRC_RANK : 1.0
        MEDIAN_CONT : 65221.405
        DEPT_NO : 115
        SALARY : 6000000
        PRC_RANK : 0.0
        MEDIAN_CONT : 6740000.0
        DEPT_NO : 115
        SALARY : 7480000
        PRC_RANK : 1.0
        MEDIAN_CONT : 6740000.0
        DEPT_NO : 120
        SALARY : 22935
        PRC_RANK : 0.0
        MEDIAN_CONT : 33620.63
        DEPT_NO : 120
        SALARY : 33620.63
        PRC_RANK : 0.5
        MEDIAN_CONT : 33620.63
        DEPT_NO : 120
        SALARY : 39224.06
        PRC_RANK : 1.0
        MEDIAN_CONT : 33620.63
        DEPT_NO : 121
        SALARY : 110000
        PRC_RANK : 0.0
        MEDIAN_CONT : 110000.0
        DEPT_NO : 123
        SALARY : 38500
        PRC_RANK : 0.0
        MEDIAN_CONT : 38500.0
        DEPT_NO : 125
        SALARY : 33000
        PRC_RANK : 0.0
        MEDIAN_CONT : 33000.0
        DEPT_NO : 130
        SALARY : 86292.94
        PRC_RANK : 0.0
        MEDIAN_CONT : 94521.47
        DEPT_NO : 130
        SALARY : 102750
        PRC_RANK : 1.0
        MEDIAN_CONT : 94521.47
        DEPT_NO : 140
        SALARY : 100914
        PRC_RANK : 0.0
        MEDIAN_CONT : 100914.0
        DEPT_NO : 180
        SALARY : 42742.5
        PRC_RANK : 0.0
        MEDIAN_CONT : 53688.75
        DEPT_NO : 180
        SALARY : 64635
        PRC_RANK : 1.0
        MEDIAN_CONT : 53688.75

        3100
        {qry_map[3100][0]}
        {qry_map[3100][1]}
        P_CONT_CORRELATED : 20.0
        P_DISC_CORRELATED : 20

        3200
        {qry_map[3200][0]}
        {qry_map[3200][1]}
        P_CONT_UNCORRELATED : 20.0

        3300
        {qry_map[3300][0]}
        {qry_map[3300][1]}
        P_CONT_CORR_DESC_ORD : 20.0

        3400
        {qry_map[3400][0]}
        {qry_map[3400][1]}
        P_CONT_NO_SUBQUERY : 2.5
        P_DISC_NO_SUBQUERY : 2.5

        3500
        {qry_map[3500][0]}
        {qry_map[3500][1]}
        W1 : 1
        P_CONT_WINDOWED : 10.0
        W1 : 2
        P_CONT_WINDOWED : 20.0
        W1 : 3
        P_CONT_WINDOWED : 30.0

        3600
        {qry_map[3600][0]}
        {qry_map[3600][1]}
        P_CONT : 20.0
        P_DISC : 20
    """

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
