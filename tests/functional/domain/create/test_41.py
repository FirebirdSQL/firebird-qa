#coding:utf-8
#
# id:           functional.domain.create.41
# title:        CREATE DOMAIN - create two domain with same name
# decription:   The creation of already existing domain must fail (SQLCODE -607).
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.domain.create.create_domain_41

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE DOMAIN test AS INTEGER;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE DOMAIN test AS VARCHAR(32);"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 23000
unsuccessful metadata update
-CREATE DOMAIN TEST failed
-violation of PRIMARY or UNIQUE KEY constraint "RDB$INDEX_2" on table "RDB$FIELDS"
-Problematic key value is ("RDB$FIELD_NAME" = 'TEST')"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

