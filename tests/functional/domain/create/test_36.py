#coding:utf-8
#
# id:           functional.domain.create.36
# title:        CREATE DOMAIN - DEFAULT CURRENT_ROLE
# decription:   Domain creation based on VARCHAR datatype with CURRENT_ROLE DEFAULT specification.
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.domain.create.create_domain_36

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE DOMAIN test VARCHAR(32) DEFAULT CURRENT_ROLE;
SHOW DOMAIN test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """TEST                            VARCHAR(32) Nullable
DEFAULT CURRENT_ROLE"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

