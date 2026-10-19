
# coding:utf-8

"""
ID:          functional.tablespace.autoddl_off.create_ts_if_not_exists
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
def test_1(act: Action, tmpdir: Path):

    ts_file = tmpdir / 'ts_file.dat'

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';
    commit;
    """
    act.isql(switches=['-q', '-n'], input=init_script)
    test_script = f"""
    CREATE TABLESPACE IF NOT EXISTS TS1 FILE '{ts_file}';
    SET LIST;
    SELECT RDB$TABLESPACE_NAME FROM RDB$TABLESPACES WHERE RDB$TABLESPACE_NAME = 'TS1';
    commit;
    """
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q', '-n'], input=test_script)

    assert act.clean_stdout == act.clean_expected_stdout
