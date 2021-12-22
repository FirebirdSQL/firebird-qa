#coding:utf-8
#
# id:           functional.domain.create.42
# title:        CREATE DOMAIN - domain name equal to existing datatype
# decription:   Domain creation must fail (SQLCODE -104) if domain name is equal to datatype name.
# tracker_id:   
# min_versions: []
# versions:     2.5.0
# qmid:         functional.domain.create.create_domain_42

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE DOMAIN INT AS VARCHAR(32);"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000

Dynamic SQL Error
-SQL error code = -104
-Token unknown - line 1, column 15
-INT"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

