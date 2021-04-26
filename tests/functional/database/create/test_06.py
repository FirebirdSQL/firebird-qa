#coding:utf-8
#
# id:           functional.database.create_06
# title:        CREATE DATABASE - PAGE SIZE 8192
# decription:   
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!PAGE_SIZE).)*$', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=8192, sql_dialect=3, init=init_script_1)

test_script_1 = """ 
    set list on;
    select mon$page_size as page_size from mon$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """        
    PAGE_SIZE                       8192
  """

@pytest.mark.version('>=3.0')
def test_create_06_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

