# coding:utf-8

"""
ID:          n/a
TITLE:       functional.tablespace.create_ts
DESCRIPTION:
"""

import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
act = isql_act('db')

expected_stdout = ""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):

    ts_file = tmpdir / 'ts_file.dat'

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';
    commit;
    """
    act.isql(switches=['-q'], input=init_script)

    act.expected_stdout = expected_stdout
    assert act.clean_stdout == act.clean_expected_stdout
