# coding:utf-8

"""
ID:          functional.tablespace.create_ts_specify_filename
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.create_ts_specify_filename
"""

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()
act = isql_act('db')


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_path: Path):

    ts_filename = 'tablespace.dat'
    ts_path = tmp_path / ts_filename

    script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_filename}';
    commit;
    """
    act.isql(switches=['-q'], input=script)

    assert ts_path.is_file()
