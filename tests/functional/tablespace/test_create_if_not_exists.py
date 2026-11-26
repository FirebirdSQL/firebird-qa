
# coding:utf-8

"""
ID:          functional.tablespace.test_create_if_not_exists
TITLE:
DESCRIPTION:
"""

import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
act = isql_act('db')

expected_stdout = """
RDB$TABLESPACE_NAME             TS1
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

        init_script = f"""
        CREATE TABLESPACE TS1 FILE '{ts_file}';
        commit;
        """
        act.reset()
        act.isql(switches=isql_switches, input=init_script)

        test_script = f"""
        CREATE TABLESPACE IF NOT EXISTS TS1 FILE '{ts_file}';
        {commit}
        SET LIST;
        SELECT RDB$TABLESPACE_NAME FROM RDB$TABLESPACES WHERE RDB$TABLESPACE_NAME = 'TS1';
        commit;
        """
        act.reset()
        act.expected_stdout = expected_stdout
        act.isql(switches=isql_switches, input=test_script)
        assert act.clean_stdout == act.clean_expected_stdout, f"AUTODDL: {autoddl}"

        cleanup_script = f"""
        DROP TABLESPACE TS1;
        commit;
        """
        act.reset()
        act.reset()
        act.isql(switches=['-q'], input=cleanup_script)
