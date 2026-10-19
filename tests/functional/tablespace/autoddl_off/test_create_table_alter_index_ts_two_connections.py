# coding:utf-8

"""
ID:          functional.tablespace.autoddl_off.create_table_alter_index_ts_two_connections
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.autoddl_off.create_table_alter_index_ts_two_connections
"""

import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
act = isql_act('db')

expected_stdout = """
ID                              123
VARCHAR_F                       summer
RDB$TABLESPACE_NAME             PRIMARY
ID                              123
VARCHAR_F                       summer
RDB$TABLESPACE_NAME             TS1
"""

expected_stderr = """
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts_file = tmpdir / 'tablespace.dat'

    db_conn = act.db.connect()

    test_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL, VARCHAR_F VARCHAR(100));

    CREATE INDEX IDX_TEST ON TEST_TABLE (ID);

    insert into test_table values (123, 'summer');

    set list on;

    select * from TEST_TABLE;

    select RDB$TABLESPACE_NAME from RDB$INDICES where RDB$INDEX_NAME='IDX_TEST';
    commit;
    """
    act.isql(switches=['-q', '-n'], input=test_script)
    stdout = act.clean_stdout + '\n'
    act.reset()

    script = """
    ALTER INDEX IDX_TEST SET TABLESPACE TO TS1;
    commit;
    """
    act.expected_stderr = expected_stderr
    act.isql(switches=['-q', '-n'], input=script)
    stderr = act.clean_stderr
    act.reset()

    db_conn.close()

    script = """
    ALTER INDEX IDX_TEST SET TABLESPACE TO TS1;

    set list on;

    select * from TEST_TABLE;

    select RDB$TABLESPACE_NAME from RDB$INDICES where RDB$INDEX_NAME='IDX_TEST';
    commit;
    """
    act.isql(switches=['-q', '-n'], input=script)
    stdout += act.clean_stdout

    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    assert stdout == act.clean_expected_stdout and stderr == act.clean_expected_stderr
