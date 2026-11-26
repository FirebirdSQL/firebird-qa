# coding:utf-8

"""
ID:          functional.tablespace.test_alter_ts
TITLE:       functional.tablespace.alter_ts
DESCRIPTION:
"""

import pytest
import shutil
from pathlib import Path
from firebird.qa import *


db = db_factory()
act = isql_act('db')

expected_stdout = """
ID                              123
INT_F                           345
FLOAT_F                         34.23
DP_F                            56.45000000000000
NUMERIC_F                       87.560000
TIMESTAMP_F                     1983-02-01 00:00:00.0000
VARCHAR_F                       summer
ID                              123
INT_F                           345
FLOAT_F                         34.23
DP_F                            56.45000000000000
NUMERIC_F                       87.560000
TIMESTAMP_F                     1983-02-01 00:00:00.0000
VARCHAR_F                       summer
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
        
        ts1_file = tmp_path / 'tablespace1.dat'
        ts1_file.unlink(missing_ok=True)
        ts2_file = tmp_path / 'tablespace2.dat'
        ts2_file.unlink(missing_ok=True)

        test_script = f"""
        CREATE TABLESPACE TS1 FILE '{ts1_file}';
        {commit}

        CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));
        {commit}

        ALTER TABLE TEST_TABLE SET TABLESPACE TS1;
        {commit}

        insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
        {commit}

        set list on;
        select * from test_table;
        commit;
        """
        act.reset()
        act.isql(switches=isql_switches, input=test_script)
        stdout = act.clean_stdout + '\n'

        shutil.copyfile(ts1_file, ts2_file)
        act.reset()
        act.isql(switches=isql_switches, input=f"ALTER TABLESPACE TS1 SET FILE TO '{ts2_file}'; {commit}")

        ts_renamefile = tmp_path / 'tablespace_rename.dat'
        ts_renamefile.unlink(missing_ok=True)
        ts1_file.rename(ts_renamefile)

        after_rename_script = """
        set list on;
        select * from test_table;    
        """
        act.reset()
        act.isql(switches=isql_switches, input=after_rename_script)
        stdout += act.clean_stdout

        act.expected_stdout = expected_stdout
        assert stdout == act.clean_expected_stdout, f"AUTODDL: {autoddl}"

        cleanup_script = f"""
        DROP TABLE TEST_TABLE;
        commit;
        DROP TABLESPACE TS1;
        commit;
        """
        act.reset()
        act.isql(switches=['-q'], input=cleanup_script)
