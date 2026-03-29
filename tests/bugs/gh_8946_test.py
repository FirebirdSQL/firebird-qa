#coding:utf-8

"""
ID:          issue-8946
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/8946
TITLE:       PERCENTILE_CONT and PERCENTILE_DISC functions #2
DESCRIPTION:
    Currently test contains only two examples from the ticket. More checks will be added later.
NOTES:
    [29.03.2026] pzotov
    Test uses DDL and data from employee DB but they have been extracted to .sql and stored in 
    files/standard_sample_databases.zip (file: "sample-DB_-_firebird.sql").
    Default names of all constraints were replaced in order to easy find appropriate table.

    Checked on 6.0.0.1858-c0190d0.
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
        PRC_RANK : 0.25
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
