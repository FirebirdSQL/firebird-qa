#coding:utf-8
#
# id:           functional.domain.drop.03
# title:        DROP DOMAIN - that doesn't exists
# decription:   DROP DOMAIN - that doesn't exists
#               Note:Bad error message (should be like "Domain TEST not exists")
#               
#               Dependencies:
#               CREATE DATABASE
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.domain.drop.drop_domain_03

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """DROP DOMAIN test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-DROP DOMAIN TEST failed
-Domain not found

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

