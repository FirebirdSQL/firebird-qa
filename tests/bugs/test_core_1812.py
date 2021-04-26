#coding:utf-8
#
# id:           bugs.core_1812
# title:        Index is not used for some date/time expressions in dialect 1
# decription:   
#                   02.02.2019. Added separate code for FB 4.0: statements like SELECT TIMESTAMP 'now' FROM RDB$DATABASE;
#                   -- can not be used anymore (Statement failed, SQLSTATE = 22018 / conversion error from string "now").
#                   Details about timezone datatype see in: doc\\sql.extensions\\README.time_zone.md
#                
# tracker_id:   CORE-1812
# min_versions: []
# versions:     4.0
# qmid:         bugs.core_1812

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=1, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (TEST INDEX (TEST_DTS))
    PLAN (TEST NATURAL)
  """

@pytest.mark.version('>=4.0')
def test_core_1812_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

