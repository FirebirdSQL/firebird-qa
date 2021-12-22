#coding:utf-8
#
# id:           bugs.core_3204
# title:        Constraint violation error of CAST is not raised inside views
# decription:   
# tracker_id:   CORE-3204
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter  view v1 as select 1 id from rdb$database;
    commit;
    set term ^;
    execute block as
    begin
      execute statement 'drop domain d1';
    when any do begin end
    end
    ^
    set term ;^
    commit;
    
    create domain d1 integer not null;
    commit;
    
    set list on;
    
    select cast(null as d1) from rdb$database; -- error: ok
    commit;
    
    create or alter view v1 as select cast(null as d1) x from rdb$database;
    commit;

    select * from v1; 
    
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    validation error for CAST, value "*** null ***"
    Statement failed, SQLSTATE = 42000
    validation error for CAST, value "*** null ***"
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

