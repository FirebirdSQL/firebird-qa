# coding:utf-8

"""
ID:          functional.tablespace.autoddl_off.create_table_ts_alter_table_ts
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.autoddl_off.create_table_ts_alter_table_ts
"""

import os
import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
substitutions = [('I/O error during .*', 'I/O error during "CreateFile (open)" operation for file'),
                 ('The system cannot find the file specified.', 'No such file or directory')]
act = isql_act('db', substitutions=substitutions)

expected_stdout = """
RDB$TABLESPACE_NAME             TS1

ID                              123
INT_F                           345
FLOAT_F                         34.23
DP_F                            56.45000000000000
NUMERIC_F                       87.560000
TIMESTAMP_F                     1983-02-01 00:00:00.0000
VARCHAR_F                       summer
ID                              344
INT_F                           45
FLOAT_F                         67.889999
DP_F                            78.89800000000000
NUMERIC_F                       78.878000
TIMESTAMP_F                     1984-11-10 00:00:00.0000
VARCHAR_F                       winter
ID                              78
INT_F                           87
FLOAT_F                         4.5999999
DP_F                            467.7687000000000
NUMERIC_F                       90.793000
TIMESTAMP_F                     1985-04-15 00:00:00.0000
VARCHAR_F                       autumn
ID                              94
INT_F                           145
FLOAT_F                         7.8699999
DP_F                            899.4560000000000
NUMERIC_F                       36.570000
TIMESTAMP_F                     1986-06-08 00:00:00.0000
VARCHAR_F                       spring

RDB$TABLESPACE_NAME             TS2
"""

expected_stderr = """
Statement failed, SQLSTATE = 08001
I/O error during "CreateFile (open)" operation for file 
-Error while trying to open file
-No such file or directory
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts1_file = tmpdir / 'tablespace1.dat'
    ts2_file = tmpdir / 'tablespace2.dat'

    script = f"""
    CREATE TABLESPACE TS1 FILE '{ts1_file}';
    CREATE TABLESPACE TS2 FILE '{ts2_file}';

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));

    ALTER TABLE TEST_TABLE SET TABLESPACE TO TS1;

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
    insert into test_table values (344, 45, 67.89, 78.898, 78.878, '10.11.1984', 'winter');
    insert into test_table values (78, 87, 4.6, 467.7687, 90.793, '15.04.1985', 'autumn');
    insert into test_table values (94, 145, 7.87, 899.456, 36.57, '08.06.1986', 'spring');

    set list on;
    select RDB$TABLESPACE_NAME from RDB$RELATIONS where RDB$RELATION_NAME='TEST_TABLE';

    ALTER TABLE TEST_TABLE SET TABLESPACE TS2;

    select * from TEST_TABLE;

    select RDB$TABLESPACE_NAME from RDB$RELATIONS where RDB$RELATION_NAME='TEST_TABLE';
    commit;
    """
    act.isql(switches=['-q', '-n'], input=script)
    stdout = act.clean_stdout
    act.reset()

    ts_renamefile = tmpdir / 'tablespace_rename.dat'
    os.rename(ts2_file, ts_renamefile)

    script = """
    set list on;
    select * from test_table;
    """
    act.expected_stderr = expected_stderr
    act.isql(switches=['-q', '-n'], input=script)
    stderr = act.clean_stderr

    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    assert stdout == act.clean_expected_stdout and stderr == act.clean_expected_stderr
