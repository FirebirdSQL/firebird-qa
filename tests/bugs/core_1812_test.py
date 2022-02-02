#coding:utf-8

"""
ID:          issue-2242
ISSUE:       2242
TITLE:       Index is not used for some date/time expressions in dialect 1
DESCRIPTION:
NOTES:
[02.02.2019] Added separate code for FB 4.0: statements like SELECT TIMESTAMP 'now' FROM RDB$DATABASE;
  -- can not be used anymore (Statement failed, SQLSTATE = 22018 / conversion error from string "now").
  Details about timezone datatype see in: doc\\sql.extensions\\README.time_zone.md
JIRA:        CORE-1812
FBTEST:      bugs.core_1812
"""

import pytest
from firebird.qa import *

# version: 3.0

init_script_1 = """
    create table t (col timestamp) ;
    create index it on t (col) ;
    commit ;
  """

db_1 = db_factory(sql_dialect=1, init=init_script_1)

test_script_1 = """
    SET PLAN ON;
    select * from t where col > timestamp 'now' - 7 ;
    select * from t where col > 'now' - 7 ;
"""

act_1 = isql_act('db_1', test_script_1)

expected_stdout_1 = """
    PLAN (T INDEX (IT))
    PLAN (T INDEX (IT))
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0

db_2 = db_factory(sql_dialect=1)

test_script_2 = """
    create table test (dts timestamp) ;
    commit;
    insert into test
    select dateadd( rand() * 10 second to localtimestamp )
    from rdb$types, rdb$types;
    commit;
    create index test_dts on test(dts);
    commit;

    set planonly;
    select * from test where dts = localtimestamp;
    select * from test where dts = current_timestamp;
"""

act_2 = isql_act('db_2', test_script_2)

expected_stdout_2 = """
    PLAN (TEST INDEX (TEST_DTS))
    PLAN (TEST NATURAL)
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout

