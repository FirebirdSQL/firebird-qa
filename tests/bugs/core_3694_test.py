#coding:utf-8
#
# id:           bugs.core_3694
# title:        internal Firebird consistency check in query with grouping by subquery+stored procedure+aggregate 
# decription:   
# tracker_id:   CORE-3694
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
    -- As of 27-apr-2015,, this error exists at least up to WI-V2.5.5.26861
    -- (not only in 2.5.1 as it is issued in the ticket).
    set term ^;
    create or alter procedure dummy_proc(val integer) returns(result integer) as
    begin
      result = val;
      suspend;
    end
    ^
    set term ;^
    commit;
    
    -- wrong query (uses an aggregate function in a group by clause)
    select ( select result from dummy_proc(sum(t.rdb$type)) ) as is_correct
          ,count(*) from rdb$types t
    group by is_correct;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

