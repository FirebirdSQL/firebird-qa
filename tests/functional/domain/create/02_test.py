#coding:utf-8
#
# id:           functional.domain.create.02
# title:        Simple domain creation based INTEGER datatype.
# decription:   Simple domain creation based INTEGER datatype.
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.domain.create.create_domain_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE DOMAIN test INTEGER;
SHOW DOMAIN test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """TEST                            INTEGER Nullable
"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

