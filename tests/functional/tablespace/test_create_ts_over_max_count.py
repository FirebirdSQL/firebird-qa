# coding:utf-8

"""
ID:          functional.tablespace.create_ts_over_max_count
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.create_ts_over_max_count
"""

from re import sub
import pytest
from pathlib import Path
from firebird.qa import *

max_count = 257

db = db_factory()
act = isql_act('db', substitutions=[('RDB\\$INDEX_\\d+', 'RDB$INDEX_XX')])

expected_stderr = """
Statement failed, SQLSTATE = 23000
unsuccessful metadata update
-CREATE TABLESPACE TS254 failed
-violation of PRIMARY or UNIQUE KEY constraint "RDB$INDEX_59" on table "SYSTEM"."RDB$TABLESPACES"
-Problematic key value is ("RDB$TABLESPACE_ID" = 3)

Statement failed, SQLSTATE = 23000
unsuccessful metadata update
-CREATE TABLESPACE TS255 failed
-violation of PRIMARY or UNIQUE KEY constraint "RDB$INDEX_59" on table "SYSTEM"."RDB$TABLESPACES"
-Problematic key value is ("RDB$TABLESPACE_ID" = 5)

Statement failed, SQLSTATE = 23000
unsuccessful metadata update
-CREATE TABLESPACE TS256 failed
-violation of PRIMARY or UNIQUE KEY constraint "RDB$INDEX_59" on table "SYSTEM"."RDB$TABLESPACES"
-Problematic key value is ("RDB$TABLESPACE_ID" = 7)

Statement failed, SQLSTATE = 23000
unsuccessful metadata update
-CREATE TABLESPACE TS257 failed
-violation of PRIMARY or UNIQUE KEY constraint "RDB$INDEX_59" on table "SYSTEM"."RDB$TABLESPACES"
-Problematic key value is ("RDB$TABLESPACE_ID" = 9)
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):

    script = ""
    for i in range(1, (max_count+1)):
        ts_files = tmpdir / 'tablespace'+str(i)+'.dat'
        script += f"CREATE TABLESPACE TS{i} FILE '{ts_files}';\n"
    act.expected_stderr = expected_stderr
    act.isql(switches=['-q'], input=script)

    assert act.clean_stderr == act.clean_expected_stderr
