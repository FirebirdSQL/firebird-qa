# coding:utf-8

"""
ID:          functional.tablespace.create_table_ts_create_index_ts_not_exists
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.create_table_ts_create_index_ts_not_exists
"""

import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()

act = isql_act('db')

expected_stderr = """
Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE INDEX "PUBLIC"."IDX_TEST" failed
-Tablespace TS1 not found
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):

    init_script = f"""
    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));
    commit;

    CREATE INDEX IDX_TEST ON TEST_TABLE (ID) TABLESPACE TS1;
    commit;
    """
    act.expected_stderr = expected_stderr
    act.isql(switches=['-q'], input=init_script)

    assert act.clean_stderr == act.clean_expected_stderr
