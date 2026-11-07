#coding:utf-8

"""
ID:          issue-8946
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/8946
TITLE:       PERCENTILE_CONT and PERCENTILE_DISC functions #2
DESCRIPTION:
    test_1 contains two examples from the ticket.
    test_2 is a regression check for a scalar sub-select in the WITHIN GROUP (ORDER BY ...)
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
        Added test_2. The value argument of a percentile aggregate is aliased from the first
        item of the WITHIN GROUP (ORDER BY ...) clause, and PercentileAggNode::dsqlCopy() passed
        only the order clause: the very same sub-select node was left in the copy, and genBlr()
        wrote its context twice into the BLR. Ad-hoc statements and views with such a statement
        used to fail at run time with "context already in use (BLR error)", and the view DDL was
        rejected at creation with "invalid request BLR at offset ...".
        Checked on 6.0.0.2447-a75c543.
"""

import pytest
import zipfile
from pathlib import Path
from firebird.qa import *
from firebird.driver import DatabaseError

db = db_factory()
substitutions = []

act = python_act('db', substitutions = substitutions)
tmp_sql = temp_file('gh_8061.tmp.sql')

# Schema and data of test_2.
init_isql = """
    recreate table pct_t1 (id integer, val numeric(15,4));
    recreate table pct_t2 (id integer, t1id integer, val integer);
    insert into pct_t1 values (1, 1.5);
    insert into pct_t1 values (2, 2.5);
    insert into pct_t1 values (3, 3.5);
    insert into pct_t2 values (1, 1, 10);
    insert into pct_t2 values (2, 2, 20);
    insert into pct_t2 values (3, 3, 30);
    commit;
    set list on;
    set count off;
"""

test_script_2 = init_isql + """
    -- correlated scalar sub-select in the WITHIN GROUP (ORDER BY ...):
    select percentile_cont(0.5) within group (order by (select max(t2.val) from pct_t2 t2 where t2.t1id = t1.id)) as c1 from pct_t1 t1;
    select percentile_disc(0.5) within group (order by (select max(t2.val) from pct_t2 t2 where t2.t1id = t1.id)) as c2 from pct_t1 t1;
    -- uncorrelated sub-select:
    select percentile_cont(0.5) within group (order by (select avg(t2.val) from pct_t2 t2)) as c3 from pct_t1 t1;
    -- sub-select with DESC:
    select percentile_cont(0.5) within group (order by (select max(t2.val) from pct_t2 t2 where t2.t1id = t1.id) desc) as c4 from pct_t1 t1;
    -- controls, no sub-select:
    select percentile_cont(0.5) within group (order by t1.val) as c5 from pct_t1 t1;
    select percentile_disc(0.5) within group (order by t1.val) as c6 from pct_t1 t1;
    -- windowed form:
    select t1.id as w1, percentile_cont(0.5) within group (order by (select max(t2.val) from pct_t2 t2 where t2.t1id = t1.id)) over (partition by t1.id) as w2 from pct_t1 t1 order by 1;
    -- the same statements in views:
    create view pct_v_cont (r) as
        select percentile_cont(0.5) within group (order by (select max(t2.val) from pct_t2 t2 where t2.t1id = t1.id)) from pct_t1 t1;
    create view pct_v_disc (r) as
        select percentile_disc(0.5) within group (order by (select max(t2.val) from pct_t2 t2 where t2.t1id = t1.id)) from pct_t1 t1;
    select * from pct_v_cont;
    select * from pct_v_disc;
"""

expected_stdout_2 = """
    C1 20.00000000000000
    C2 20
    C3 20.00000000000000
    C4 20.00000000000000
    C5 2.500000000000000
    C6 2.5000
    W1 1
    W2 10.00000000000000
    W1 2
    W2 20.00000000000000
    W1 3
    W2 30.00000000000000
    R 20.00000000000000
    R 20
"""

act_2 = isql_act('db', test_script_2, substitutions=[('[ \t]+', ' ')])


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_sql: Path, capsys):
    employee_data_sql = zipfile.Path(act.files_dir / 'standard_sample_databases.zip', at='sample-DB_-_firebird.sql')
    tmp_sql.write_bytes(employee_data_sql.read_bytes())

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
    query_map = {
        1000 : (
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
        2000 : (
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
    }


    with act.db.connect() as con:
        cur = con.cursor()
        for q_idx, q_tuple in query_map.items():
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
    expected_stdout_6x = f"""
        1000
        {query_map[1000][0]}
        {query_map[1000][1]}
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
        {query_map[2000][0]}
        {query_map[2000][1]}
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

    """

    act.expected_stdout = expected_stdout_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout


@pytest.mark.ai
@pytest.mark.version('>=6.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout
    assert act_2.clean_stderr == ''
