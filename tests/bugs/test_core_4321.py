#coding:utf-8
#
# id:           bugs.core_4321
# title:        Regression: ISQL does not destroy the SQL statement
# decription:   
# tracker_id:   CORE-4321
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- NB: 2.1.7 FAILED, output contains '4' for select count(*) ...
    set list on
    select 1 x from rdb$database;
    select 1 x from rdb$database;
    select 1 x from rdb$database;
    select 1 x from rdb$database;
    
    select count(*) c from mon$statements s 
    where s.mon$sql_text containing 'select 1 x' -- 08-may-2017: need for 4.0 Classic! Currently there is also query with RDB$AUTH_MAPPING data in mon$statements
    ;
    commit;
    select count(*) c from mon$statements s 
    where s.mon$sql_text containing 'select 1 x'
    ;
    
    select 1 x from rdb$database;
    select 1 x from rdb$database;
    select 1 x from rdb$database;
    select 1 x from rdb$database;
    
    select count(*) c from mon$statements s 
    where s.mon$sql_text containing 'select 1 x'
    ;
    commit;
    
    select count(*) c from mon$statements s 
    where s.mon$sql_text containing 'select 1 x'
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X                               1
    X                               1
    X                               1
    C                               1
    C                               1
    X                               1
    X                               1
    X                               1
    X                               1
    C                               1
    C                               1
  """

@pytest.mark.version('>=2.5')
def test_core_4321_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

