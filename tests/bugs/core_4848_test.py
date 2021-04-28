#coding:utf-8
#
# id:           bugs.core_4848
# title:        MERGE ... WHEN NOT MATCHED ... RETURNING returns wrong (non-null) values when no insert is performed
# decription:   
# tracker_id:   CORE-4848
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=1, init=init_script_1)

test_script_1 = """
    set list on;
    recreate table t1 (n1 integer, n2 integer);
    
    -- Case 1:
    merge into t1
    using (
        select 1 x
        from rdb$database
        where 1 = 0
    ) on 1 = 1
    when not matched then
        insert values (1, 11)
        returning n1, n2;
    
    -- Case 2:
    merge into t1
    using (
        select 1 x
        from rdb$database
        where 1 = 1
    ) on 1 = 0
    when not matched and 1 = 0 then
        insert values (1, 11)
        returning n1, n2;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    N1                              <null>
    N2                              <null>

    N1                              <null>
    N2                              <null>
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

