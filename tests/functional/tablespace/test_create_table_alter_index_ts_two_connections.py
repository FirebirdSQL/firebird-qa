# coding:utf-8

"""
ID:          functional.tablespace.test_create_table_alter_index_ts_two_connections
TITLE:       functional.tablespace.create_table_alter_index_ts_two_connections
DESCRIPTION:
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
def test_1(act: Action, tmp_path: Path):
    for autoddl in (True, False):
        if autoddl:
            commit = 'commit;'
            isql_switches = ['-q']
        else:
            commit = ''
            isql_switches = ['-q', '-n']
        
        ts_file = tmp_path / 'tablespace1.dat'
        ts_file.unlink(missing_ok=True)

        db_conn = act.db.connect()

        test_script = f"""
        CREATE TABLESPACE TS1 FILE '{ts_file}';
        {commit}

        CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL, VARCHAR_F VARCHAR(100));
        {commit}

        CREATE INDEX IDX_TEST ON TEST_TABLE (ID);
        {commit}

        insert into test_table values (123, 'summer');
        {commit}

        set list on;

        select * from TEST_TABLE;

        select RDB$TABLESPACE_NAME from RDB$INDICES where RDB$INDEX_NAME='IDX_TEST';
        commit;
        """
        act.reset()
        act.isql(switches=isql_switches, input=test_script)
        stdout = act.clean_stdout + '\n'

        script = """
        ALTER INDEX IDX_TEST SET TABLESPACE TO TS1;
        commit;
        """
        act.reset()
        act.expected_stderr = expected_stderr
        act.isql(switches=isql_switches, input=script)
        stderr = act.clean_stderr

        db_conn.close()

        script = f"""
        ALTER INDEX IDX_TEST SET TABLESPACE TO TS1;
        {commit}

        set list on;

        select * from TEST_TABLE;

        select RDB$TABLESPACE_NAME from RDB$INDICES where RDB$INDEX_NAME='IDX_TEST';
        commit;
        """
        act.reset()
        act.isql(switches=isql_switches, input=script)
        stdout += act.clean_stdout

        act.expected_stdout = expected_stdout
        act.expected_stderr = expected_stderr
        assert stdout == act.clean_expected_stdout and stderr == act.clean_expected_stderr, f"AUTODDL: {autoddl}"

        cleanup_script = f"""
        DROP TABLE TEST_TABLE;
        commit;
        DROP TABLESPACE TS1;
        commit;
        """
        act.reset()
        act.isql(switches=['-q'], input=cleanup_script)
