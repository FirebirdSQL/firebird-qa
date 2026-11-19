# coding:utf-8

"""
ID:          functional.tablespace.test_create_ts_max_count
TITLE:       functional.tablespace.create_ts_max_count
DESCRIPTION:
"""

import pytest
from pathlib import Path
from firebird.qa import *

max_count = 253

db = db_factory()
act = isql_act('db')

expected_stdout = ""


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
        act.isql(switches=isql_switches, input=script)

        act.expected_stdout = expected_stdout
        assert act.clean_stdout == act.clean_expected_stdout, f"AUTODDL: {autoddl}"

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
