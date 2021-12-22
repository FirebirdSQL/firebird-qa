#coding:utf-8
#
# id:           functional.database.create.07
# title:        CREATE DATABASE with PAGE_SIZE=16384: check actual size of page in the created database.
# decription:   
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
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

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

