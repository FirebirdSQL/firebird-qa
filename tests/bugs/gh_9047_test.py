#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9047
TITLE:       Add a GROUPS unit for window frames
DESCRIPTION:
    Test uses DDL and data from employee DB but they have been extracted to .sql and stored in 
    files/standard_sample_databases.zip (file: "sample-DB_-_firebird.sql").
    Default names of all constraints were replaced in order to easy find appropriate table.
NOTES:
    [09.06.2026] pzotov
    Currently test contains only example from the ticket and applies it to standard example database 'employee'
    which has been exported as SQL script (metadata+data) in the $QA_HOME/files/standard_sample_databases.zip.
    Other examples will be added later.
    Checked on 6.0.0.1999-c8bc46b.
"""
import zipfile
from pathlib import Path
from firebird.driver import DatabaseError

import pytest
from firebird.qa import *

db = db_factory()
act = python_act('db')

tmp_sql = temp_file('gh_9047.tmp.sql')

query_map = {
    1000 : (
              """
                select emp_no, hire_date
                    -- include current & three previous rows
                  , count(*) over ( order by hire_date rows 3 preceding ) prev3_rows
                    -- include all rows between hire_date - 3 and hire_date for the current row
                  , count(*) over ( order by hire_date range 3 preceding ) prev3_days
                    -- include all rows with the any of the previous three and current hire_dates
                  , count(*) over ( order by hire_date groups 3 preceding ) prev3_values
                from employee
                where  hire_date >= date '1991-02-01'
                order by emp_no
                fetch first 5 rows only
                ;
              """
             ,'Basic test from the ticket'
           )
}

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_sql: Path, capsys):
    employee_data_sql = zipfile.Path(act.files_dir / 'standard_sample_databases.zip', at='sample-DB_-_firebird.sql')
    tmp_sql.write_bytes(employee_data_sql.read_bytes())

    act.isql(switches = ['-q'], input_file = tmp_sql, combine_output = True)
    if act.return_code == 0:
        with act.db.connect() as con:
            cur = con.cursor()
            for q_idx, q_tuple in query_map.items():
                test_sql, qry_comment = q_tuple[:2]
                print(q_idx)
                print(test_sql)
                print(qry_comment)
                try:
                    ps = cur.prepare(test_sql)
                    cur.execute(ps)
                    ccol=cur.description
                    for r in cur:
                        for i in range(0,len(ccol)):
                            print( ccol[i][0],':', r[i])
                except DatabaseError as e:
                    print(e.__str__())
                    print(e.gds_codes)
    else:
        # If retcode !=0 then we can print the whole output of failed gbak:
        print('Initial script failed, check output:')
        for line in act.clean_stdout.splitlines():
            print(line)
    #act.reset()

    act.expected_stdout = f"""
        1000
        {query_map[1000][0]}
        {query_map[1000][1]}
        EMP_NO : 28
        HIRE_DATE : 1991-02-01 00:00:00
        PREV3_ROWS : 1
        PREV3_DAYS : 1
        PREV3_VALUES : 1

        EMP_NO : 29
        HIRE_DATE : 1991-02-18 00:00:00
        PREV3_ROWS : 2
        PREV3_DAYS : 1
        PREV3_VALUES : 2

        EMP_NO : 34
        HIRE_DATE : 1991-03-21 00:00:00
        PREV3_ROWS : 3
        PREV3_DAYS : 1
        PREV3_VALUES : 3

        EMP_NO : 36
        HIRE_DATE : 1991-04-25 00:00:00
        PREV3_ROWS : 4
        PREV3_DAYS : 2
        PREV3_VALUES : 5

        EMP_NO : 37
        HIRE_DATE : 1991-04-25 00:00:00
        PREV3_ROWS : 4
        PREV3_DAYS : 2
        PREV3_VALUES : 5
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
