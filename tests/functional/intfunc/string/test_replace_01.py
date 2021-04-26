#coding:utf-8
#
# id:           functional.intfunc.string.replace_01
# title:        test for REPLACE  function
# decription:    REPLACE( <stringtosearch>, <findstring>, <replstring> )
#               
#               Replaces all occurrences of <findstring> in <stringtosearch> with <replstring>.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.string.replace_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ select REPLACE('toto','o','i') from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """      REPLACE
      =======
      titi"""

@pytest.mark.version('>=2.1')
def test_replace_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

