# coding:utf-8

"""
ID:          functional.tablespace.autoddl_off.alter_ts_invalid_file
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.autoddl_off.alter_ts_invalid_file
"""

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()
substitutions = [
    ('/.*tablespace', 'tablespace'),
    ('.:.*tablespace', 'tablespace'),
    ('-Error while trying to read from file', '-File size is less than expected'),
    ('-Reached the end of the file.', '')
    ]
act = isql_act('db', substitutions=substitutions)

expected_stdout = """
RDB$FILE_NAME                   tablespace1.dat

ID                              1
NAME                            One
ID                              2
NAME                            Two

RDB$FILE_NAME                   tablespace2.dat

Statement failed, SQLSTATE = 08001
I/O error during "read" operation for file "tablespace2.dat"
-File size is less than expected

RDB$FILE_NAME                   tablespace2.dat

Statement failed, SQLSTATE = 08001
I/O error during "read" operation for file "tablespace2.dat"
-File size is less than expected
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts1_file = tmpdir / 'tablespace1.dat'
    ts2_file = tmpdir / 'tablespace2.dat'

    ts2_file.write_text('Text', encoding='utf-8')

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts1_file}';

    CREATE TABLE TEST_TABLE(ID INT, NAME VARCHAR(10)) TABLESPACE TS1;

    insert into test_table values (1, 'One');
    insert into test_table values (2, 'Two');

    set list on;
    select RDB$FILE_NAME from RDB$RELATIONS as rl left join RDB$TABLESPACES as ts ON rl.RDB$TABLESPACE_NAME=ts.RDB$TABLESPACE_NAME where RDB$RELATION_NAME='TEST_TABLE';
    select * from test_table;
    commit;
    """
    act.isql(switches=['-q', '-n'], input=init_script)
    stdout = act.clean_stdout + '\n'
    act.reset()

    script = f"""
    ALTER TABLESPACE TS1 SET FILE TO '{ts2_file}';
    set list on;
    select RDB$FILE_NAME from RDB$RELATIONS as rl left join RDB$TABLESPACES as ts ON rl.RDB$TABLESPACE_NAME=ts.RDB$TABLESPACE_NAME where RDB$RELATION_NAME='TEST_TABLE';
    select * from test_table;
    commit;
    """
    act.isql(switches=['-q', '-n'], input=script, combine_output=True)
    stdout += act.clean_stdout + '\n'
    act.reset()

    script = """
    set list on;
    select RDB$FILE_NAME from RDB$RELATIONS as rl left join RDB$TABLESPACES as ts ON rl.RDB$TABLESPACE_NAME=ts.RDB$TABLESPACE_NAME where RDB$RELATION_NAME='TEST_TABLE';
    select * from test_table;
    """
    act.isql(switches=['-q', '-n'], input=script, combine_output=True)
    stdout += act.clean_stdout
    act.reset()

    script = f"""
    ALTER TABLESPACE TS1 SET FILE TO '{ts1_file}';
    commit;
    """
    act.isql(switches=['-q', '-n'], input=script, combine_output=True)
    stdout += act.clean_stdout

    act.expected_stdout = expected_stdout
    assert stdout == act.clean_expected_stdout
