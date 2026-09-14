# coding:utf-8

"""
ID:          functional.tablespace.drop_ts_failed_index_dependency
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.drop_ts_failed_index_dependency
"""

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()
act = isql_act('db')

expected_stdout = """
ID                              123
VARCHAR_F                       summer

RDB$INDEX_NAME                  IDX_TEST
RDB$TABLESPACE_NAME             TS1

Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-DROP TABLESPACE TS1 failed
-cannot delete
-TABLESPACE TS1
-there are 1 dependencies

ID                              123
VARCHAR_F                       summer
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):

    ts_file = tmpdir / 'tablespace.dat'

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';
    commit;

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,VARCHAR_F VARCHAR(100));
    commit;

    CREATE INDEX IDX_TEST ON TEST_TABLE (ID) TABLESPACE TS1;
    commit;

    insert into test_table values (123, 'summer');
    commit;

    set list on;
    select * from TEST_TABLE;
    select RDB$INDEX_NAME from RDB$INDICES where RDB$RELATION_NAME='TEST_TABLE';
    select RDB$TABLESPACE_NAME from RDB$INDICES where RDB$INDEX_NAME='IDX_TEST';

    drop TABLESPACE TS1;
    drop index IDX_TEST;
    drop TABLESPACE TS1;

    select * from TEST_TABLE;
    """
    act.isql(switches=['-q'], input=init_script, combine_output=True)

    act.expected_stdout = expected_stdout
    assert act.clean_stdout == act.clean_expected_stdout
