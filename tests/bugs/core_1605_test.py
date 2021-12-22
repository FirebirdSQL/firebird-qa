#coding:utf-8
#
# id:           bugs.core_1605
# title:        Bugcheck 232 (invalid operation) for an aggregated query
# decription:   
# tracker_id:   CORE-1605
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
    recreate table test (id int);
    
    set term ^;
    create or alter procedure sp_test (id int) returns (result int) as
    begin
      result = id * id;
      suspend;
    end
    ^
    
    set term ;^
    commit;
    
    insert into test values(1);
    insert into test values(2);
    insert into test values(3);
    commit;
    
    select
        sum( id ),
        sum( (select result from sp_test(id)) )
    from test
    group by 2;
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

