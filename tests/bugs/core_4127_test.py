#coding:utf-8
#
# id:           bugs.core_4127
# title:        Server crashes instead of reporting the error "key size exceeds implementation restriction"
# decription:
# tracker_id:   CORE-4127
# min_versions: ['2.5.3']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table tab1 (col1 int, col2 char(10));
    create index itab1 on tab1 (col1, col2);
    commit;
    insert into tab1 values(1, 'a');
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select * from tab1
    where col1 = 1 and col2 = rpad('a', 32765)
    union all
    -- This part of query will NOT raise
    -- Statement failed, SQLSTATE = 54000
    -- arithmetic exception, numeric overflow, or string truncation
    -- -Implementation limit exceeded
    -- since WI-V3.0.0.31981
    select * from tab1
    where col1 = 1 and col2 = rpad('a', 32766);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    COL1                            1
    COL2                            a
    COL1                            1
    COL2                            a
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

