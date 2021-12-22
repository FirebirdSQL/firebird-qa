#coding:utf-8
#
# id:           functional.domain.drop.01
# title:        DROP DOMAIN
# decription:   DROP DOMAIN
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE DOMAIN
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.domain.drop.drop_domain_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE DOMAIN test SMALLINT;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """DROP DOMAIN test;
SHOW DOMAIN test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """There is no domain TEST in this database"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

