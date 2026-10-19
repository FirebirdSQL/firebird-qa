# coding:utf-8

"""
ID:          functional.tablespace.autoddl_off.create_table_ts_primary
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.autoddl_off.create_table_ts_primary
"""

import pytest
from firebird.qa import *


db = db_factory()
act = isql_act('db')

expected_stdout = """
ID                              123
INT_F                           345
FLOAT_F                         34.23
DP_F                            56.45000000000000
NUMERIC_F                       87.560000
TIMESTAMP_F                     1983-02-01 00:00:00.0000
VARCHAR_F                       summer
RDB$TABLESPACE_NAME             PRIMARY
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action):

    script = f"""
    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100)) TABLESPACE PRIMARY;

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');

    set list on;
    select * from test_table;
    select RDB$TABLESPACE_NAME from RDB$RELATIONS where RDB$RELATION_NAME='TEST_TABLE';
    commit;
    """
    act.isql(switches=['-q', '-n'], input=script)

    act.expected_stdout = expected_stdout
    assert act.clean_stdout == act.clean_expected_stdout
