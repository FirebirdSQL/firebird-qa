#coding:utf-8
#
# id:           functional.domain.drop_02
# title:        DROP DOMAIN - in use
# decription:   DROP DOMAIN - that was use
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE DOMAIN
#               CREATE TABLE
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.domain.drop.drop_domain_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE DOMAIN test SMALLINT;
CREATE TABLE tb( id test);"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """DROP DOMAIN test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-DROP DOMAIN TEST failed
-Domain TEST is used in table TB (local name ID) and cannot be dropped

"""

@pytest.mark.version('>=3.0')
def test_drop_02_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

