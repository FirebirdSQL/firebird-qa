# coding:utf-8

"""
ID:          functional.tablespace.create_ts_max_count
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.create_ts_max_count
"""

import pytest
from pathlib import Path
from firebird.qa import *

max_count = 253

db = db_factory()
act = isql_act('db')

expected_stdout = ""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):

    script = ""
    for i in range(1, (max_count+1)):
        ts_files = tmpdir / 'tablespace'+str(i)+'.dat'
        script += f"CREATE TABLESPACE TS{i} FILE '{ts_files}';\n"
    act.isql(switches=['-q'], input=script)

    act.expected_stdout = expected_stdout
    assert act.clean_stdout == act.clean_expected_stdout
