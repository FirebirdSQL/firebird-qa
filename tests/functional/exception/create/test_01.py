#coding:utf-8
#
# id:           functional.exception.create.01
# title:        CREATE EXCEPTION
# decription:   CREATE EXCEPTION
#               
#               Dependencies:
#               CREATE DATABASE
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.exception.create.create_exception_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create exception test 'message to show';
    commit;
    
    set list on;
    set width exc_name 31;
    set width exc_msg 80;
    select
        e.rdb$exception_name exc_name
        ,e.rdb$exception_number exc_number
        ,e.rdb$message exc_msg
    from rdb$exceptions e;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    EXC_NAME                        TEST                                                                                         
    EXC_NUMBER                      1
    EXC_MSG                         message to show
  """

@pytest.mark.version('>=2.0')
def test_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

