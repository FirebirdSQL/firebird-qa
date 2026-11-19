# coding:utf-8

"""
ID:          functional.tablespace.test_alter_ts_new_file
TITLE:       functional.tablespace.alter_ts_new_file
DESCRIPTION:
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

        CREATE TABLE TEST_TABLE(ID INT, NAME VARCHAR(10)) TABLESPACE TS1;
        {commit}

        insert into test_table values (1, 'One');
        insert into test_table values (2, 'Two');
        {commit}

        set list on;
        select RDB$FILE_NAME from RDB$RELATIONS as rl left join RDB$TABLESPACES as ts ON rl.RDB$TABLESPACE_NAME=ts.RDB$TABLESPACE_NAME where RDB$RELATION_NAME='TEST_TABLE';
        select * from test_table;
        commit;
        """
        act.reset()
        act.isql(switches=isql_switches, input=test_script)
        stdout = act.clean_stdout + '\n'

        shutil.copyfile(ts1_file, ts2_file)

        script = f"""
        set list on;
        update test_table set NAME='So much';
        {commit}
        set list on;
        select * from test_table;
        commit;
        """
        act.reset()
        act.isql(switches=isql_switches, input=script)
        stdout += act.clean_stdout + '\n'

        script = f"""
        set list on;
        ALTER TABLESPACE TS1 SET FILE TO '{ts2_file}';
        {commit}
        select RDB$FILE_NAME from RDB$RELATIONS as rl left join RDB$TABLESPACES as ts ON rl.RDB$TABLESPACE_NAME=ts.RDB$TABLESPACE_NAME where RDB$RELATION_NAME='TEST_TABLE';
        select * from test_table;
        commit;
        """
        act.reset()
        act.isql(switches=isql_switches, input=script)
        stdout += act.clean_stdout + '\n'

        script = f"""
        set list on;
        select RDB$FILE_NAME from RDB$RELATIONS as rl left join RDB$TABLESPACES as ts ON rl.RDB$TABLESPACE_NAME=ts.RDB$TABLESPACE_NAME where RDB$RELATION_NAME='TEST_TABLE';
        select * from test_table;
        commit;
        """
        act.reset()
        act.isql(switches=isql_switches, input=script)
        stdout += act.clean_stdout

        script = f"""
        ALTER TABLESPACE TS1 SET FILE TO '{ts1_file}';
        commit;
        """
        act.reset()
        act.isql(switches=isql_switches, input=script)

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
