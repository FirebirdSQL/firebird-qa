#coding:utf-8
#
# id:           bugs.core_1312
# title:        A remote attacker can check, if a file is present in the system, running firebird server
# decription:   Check if password validation is done as soon as possible
# tracker_id:   CORE-1312
# min_versions: []
# versions:     2.5.0
# qmid:         bugs.core_1312-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    commit;
    connect 'localhost:bla' user 'qqq' password 'zzz';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 28000
Your user name and password are not defined. Ask your database administrator to set up a Firebird login.
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

