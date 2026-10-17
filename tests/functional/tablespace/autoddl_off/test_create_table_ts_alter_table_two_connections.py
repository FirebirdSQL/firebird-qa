# coding:utf-8

"""
ID:          functional.tablespace.autoddl_off.create_table_ts_alter_table_two_connections
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.autoddl_off.create_table_ts_alter_table_two_connections
"""

import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
act = isql_act('db')

expected_stdout = """
ID                              123
VARCHAR_F                       summer
RDB$TABLESPACE_NAME             TS1
ID                              123
VARCHAR_F                       summer
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts_file = tmpdir / 'tablespace.dat'

    db_conn = act.db.connect()

    script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL, VARCHAR_F VARCHAR(100));

    insert into test_table values (123, 'summer');

    set list on;
    select * from TEST_TABLE;

    ALTER TABLE TEST_TABLE SET TABLESPACE TS1;
    commit;
    """
    act.isql(switches=['-q', '-n'], input=script, combine_output=True)
    stdout = act.clean_stdout + '\n'
    act.reset()

    db_conn.close()

    script = """
    ALTER TABLE TEST_TABLE SET TABLESPACE TS1;

    set list on;
    select RDB$TABLESPACE_NAME from RDB$RELATIONS where RDB$RELATION_NAME='TEST_TABLE';

    select * from TEST_TABLE;
    commit;
    """
    act.isql(switches=['-q', '-n'], input=script, combine_output=True)
    stdout += act.clean_stdout

    act.expected_stdout = expected_stdout
    assert stdout == act.clean_expected_stdout
