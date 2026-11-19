# coding:utf-8

"""
ID:          functional.tablespace.test_drop_ts_failed_index_dependency
TITLE:       functional.tablespace.drop_ts_failed_index_dependency
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

RDB$INDEX_NAME                  IDX_TEST
RDB$TABLESPACE_NAME             TS1

Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-DROP TABLESPACE TS1 failed
-cannot delete
-TABLESPACE TS1
-there are 1 dependencies

ID                              123
VARCHAR_F                       summer
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_path: Path):
    for autoddl in (True, False):
        if autoddl:
            on_commit = 'commit;'
            off_commit = ''
            isql_switches = ['-q']
        else:
            on_commit = ''
            off_commit = 'commit;'
            isql_switches = ['-q', '-n']
        
        ts_file = tmp_path / 'tablespace1.dat'
        ts_file.unlink(missing_ok=True)

        init_script = f"""
        CREATE TABLESPACE TS1 FILE '{ts_file}';
        {on_commit}

        CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,VARCHAR_F VARCHAR(100));
        {on_commit}

        CREATE INDEX IDX_TEST ON TEST_TABLE (ID) TABLESPACE TS1;
        {on_commit}

        insert into test_table values (123, 'summer');
        {on_commit}

        set list on;
        select * from TEST_TABLE;
        select RDB$INDEX_NAME from RDB$INDICES where RDB$RELATION_NAME='TEST_TABLE';
        select RDB$TABLESPACE_NAME from RDB$INDICES where RDB$INDEX_NAME='IDX_TEST';
        {off_commit}
        
        drop TABLESPACE TS1;
        {off_commit}
        drop index IDX_TEST;
        {off_commit}
        drop TABLESPACE TS1;
        {off_commit}

        select * from TEST_TABLE;
        commit;
        """
        act.reset()
        act.isql(switches=isql_switches, input=init_script, combine_output=True)

        act.expected_stdout = expected_stdout
        assert act.clean_stdout == act.clean_expected_stdout, f"AUTODDL: {autoddl}"

        cleanup_script = f"""
        DROP TABLE TEST_TABLE;
        commit;
        """
        act.reset()
        act.isql(switches=['-q'], input=cleanup_script)
