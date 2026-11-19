# coding:utf-8

"""
ID:          functional.tablespace.test_create_ts_over_max_count
TITLE:       functional.tablespace.create_ts_over_max_count
DESCRIPTION:
"""

from re import sub
import pytest
from pathlib import Path
from firebird.qa import *

max_count = 257

substitutions = [
    ('RDB\\$INDEX_\\d+', 'RDB$INDEX_XX'),
    ('"RDB\\$TABLESPACE_ID" = \\d+', '"RDB$TABLESPACE_ID" = X')
]

db = db_factory()
act = isql_act('db', substitutions=substitutions)

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
def test_1(act: Action, tmp_path: Path):
    for autoddl in (True, False):
        if autoddl:
            rollback = 'rollback;'
            isql_switches = ['-q']
        else:
            rollback = ''
            isql_switches = ['-q', '-n']

        script = ""
        for i in range(1, (max_count+1)):
            ts_files = tmp_path / ('tablespace'+str(i)+'.dat')
            ts_files.unlink(missing_ok=True)
            script += f"CREATE TABLESPACE TS{i} FILE '{ts_files}';\n"
        script += rollback
        act.reset()
        act.expected_stderr = expected_stderr
        act.isql(switches=isql_switches, input=script)

        assert act.clean_stderr == act.clean_expected_stderr, f"AUTODDL: {autoddl}"

        cleanup_script = f"""       
        set term ^;
        EXECUTE BLOCK
        AS
        DECLARE VARIABLE TS_NAME VARCHAR(63);
        BEGIN
        FOR SELECT RDB$TABLESPACE_NAME
            FROM RDB$TABLESPACES
            WHERE rdb$system_flag = 0
            INTO :TS_NAME
        DO
            EXECUTE STATEMENT 'DROP TABLESPACE "' || TS_NAME || '"';
        END^
        set term ;^
        commit;
        """
        act.reset()
        act.isql(switches=['-q'], input=cleanup_script)


