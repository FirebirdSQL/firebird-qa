# coding:utf-8

"""
ID:          n/a
TITLE:       functional.tablespace.create_ts_failed
DESCRIPTION:
"""

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()
substitutions = [('file.*exists', 'file exists')]
act = isql_act('db', substitutions=substitutions)

expected_stderr = """
Statement failed, SQLSTATE = 08001
unsuccessful metadata update
-CREATE TABLESPACE TS1 failed
-Tablespace file exists
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path, tmp_path: Path):

    ts_file = tmpdir / 'tablespace.dat'

    open(ts_file, "w").close()

    script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';
    commit;
    """
    act.expected_stderr = expected_stderr
    act.isql(switches=['-q'], input=script)

    assert act.clean_stderr == act.clean_expected_stderr
