#coding:utf-8
#
# id:           functional.intfunc.binary.and_01
# title:        New Built-in Functions, Firebird 2.1 : BIN_AND( <number> [, <number> ...] )
# decription:   test of BIN_AND
#               
#               Returns the result of a binary AND operation performed on all arguments.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.binary.bin_and_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select BIN_AND( 1, 1) from rdb$database;

select BIN_AND( 1, 0) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """     BIN_AND
============
           1


     BIN_AND
============
           0


"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

