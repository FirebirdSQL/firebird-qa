#coding:utf-8
#
# id:           functional.database.create_07
# title:        CREATE DATABASE - PAGE SIZE 16384
# decription:   
# tracker_id:   
# min_versions: []
# versions:     3.0, 4.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!PAGE_SIZE).)*$', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=16384, sql_dialect=3, init=init_script_1)

test_script_1 = """ 
    set list on;
    select mon$page_size as page_size from mon$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """        
    PAGE_SIZE                       16384
  """

@pytest.mark.version('>=3.0,<4.0')
def test_create_07_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = [('^((?!PAGE_SIZE).)*$', '')]

init_script_2 = """"""

db_2 = db_factory(page_size=32768, sql_dialect=3, init=init_script_2)

test_script_2 = """ 
    set list on;
    select mon$page_size as page_size from mon$database;
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """        
    PAGE_SIZE                       32768
  """

@pytest.mark.version('>=4.0')
def test_create_07_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

