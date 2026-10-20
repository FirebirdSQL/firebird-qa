# coding:utf-8

"""
ID:          functional.tablespace.alter_ts_new_file
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.alter_ts_new_file
"""

import pytest
import shutil
from pathlib import Path
from firebird.qa import *


db = db_factory()
substitutions = [('/.*tablespace', 'tablespace'), ('.:.*tablespace', 'tablespace')]
act = isql_act('db', substitutions=substitutions)

expected_stdout = """
RDB$FILE_NAME                   tablespace1.dat

ID                              1
NAME                            One
ID                              2
NAME                            Two

ID                              1
NAME                            So much
ID                              2
NAME                            So much

RDB$FILE_NAME                   tablespace2.dat

ID                              1
NAME                            One
ID                              2
NAME                            Two

RDB$FILE_NAME                   tablespace2.dat

ID                              1
NAME                            One
ID                              2
NAME                            Two
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts1_file = tmpdir / 'tablespace1.dat'
    ts2_file = tmpdir / 'tablespace2.dat'

    test_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts1_file}';
    commit;

    CREATE TABLE TEST_TABLE(ID INT, NAME VARCHAR(10)) TABLESPACE TS1;
    commit;

    insert into test_table values (1, 'One');
    insert into test_table values (2, 'Two');
    commit;

    set list on;
    select RDB$FILE_NAME from RDB$RELATIONS as rl left join RDB$TABLESPACES as ts ON rl.RDB$TABLESPACE_NAME=ts.RDB$TABLESPACE_NAME where RDB$RELATION_NAME='TEST_TABLE';
    select * from test_table;
    """
    act.isql(switches=['-q'], input=test_script)
    stdout = act.clean_stdout + '\n'
    act.reset()

    shutil.copyfile(ts1_file, ts2_file)

    script = """
    set list on;
    update test_table set NAME='So much';
    commit;
    set list on;
    select * from test_table;
    """
    act.isql(switches=['-q'], input=script)
    stdout += act.clean_stdout + '\n'
    act.reset()

    script = f"""
    set list on;
    ALTER TABLESPACE TS1 SET FILE TO '{ts2_file}';
    commit;
    select RDB$FILE_NAME from RDB$RELATIONS as rl left join RDB$TABLESPACES as ts ON rl.RDB$TABLESPACE_NAME=ts.RDB$TABLESPACE_NAME where RDB$RELATION_NAME='TEST_TABLE';
    select * from test_table;
    """
    act.isql(switches=['-q'], input=script)
    stdout += act.clean_stdout + '\n'
    act.reset()

    script = """
    set list on;
    select RDB$FILE_NAME from RDB$RELATIONS as rl left join RDB$TABLESPACES as ts ON rl.RDB$TABLESPACE_NAME=ts.RDB$TABLESPACE_NAME where RDB$RELATION_NAME='TEST_TABLE';
    select * from test_table;
    commit;
    """
    act.isql(switches=['-q'], input=script)
    stdout += act.clean_stdout

    script = f"""
    ALTER TABLESPACE TS1 SET FILE TO '{ts1_file}';
    commit;
    """
    act.isql(switches=['-q'], input=script)

    act.expected_stdout = expected_stdout
    assert stdout == act.clean_expected_stdout
