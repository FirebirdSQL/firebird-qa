#coding:utf-8
#
# id:           functional.intfunc.string.ascii_01
# title:        New Built-in Functions, Firebird 2.1 : ASCII_CHAR( <number> )
# decription:   test of ASCII_CHAR
#               
#               Returns the ASCII character with the specified code. The argument to ASCII_CHAR must be in the range 0 to 255. The result is returned in character set NONE.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.string.ascii_char_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select ASCII_CHAR( 065 ) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """ASCII_CHAR
==========
A

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

