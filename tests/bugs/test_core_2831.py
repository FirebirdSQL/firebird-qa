#coding:utf-8
#
# id:           bugs.core_2831
# title:        isql shouldn't display db and user name when extracting a script
# decription:   
# tracker_id:   CORE-2831
# min_versions: ['2.0.6', '2.1.4', '2.5']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!Database:|User:).)*$', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# #
#  runProgram('isql',['-x',dsn,'-user',user_name,'-pass',user_password])
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_core_2831_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


