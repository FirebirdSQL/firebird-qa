#coding:utf-8
#
# id:           bugs.core_4131
# title:        Error when processing an empty data set by window function, if reading indexed
# decription:   
# tracker_id:   CORE-4131
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(x char(31) character set unicode_fss unique using index test_x);
    commit;
    insert into test values('qwerty');
    commit;
    
    set list on;
    set plan on;
    select row_number() over(order by x) as rn, x
    from test 
    where x = 'qwerty'
    ;
    -- 3.0.0.30472:
    -- cursor identified in the UPDATE or DELETE statement is not positioned on a row. no current record for fetch operation
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN SORT (TEST INDEX (TEST_X))
    RN                              1
    X                               qwerty
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

