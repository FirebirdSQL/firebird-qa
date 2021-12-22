#coding:utf-8
#
# id:           functional.domain.alter.05
# title:        ALTER DOMAIN - Alter domain that doesn't exists
# decription:   
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.domain.alter.alter_domain_05

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE DOMAIN test VARCHAR(63);"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ALTER DOMAIN notexists DROP CONSTRAINT;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-ALTER DOMAIN NOTEXISTS failed
-Domain not found
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

