#coding:utf-8
#
# id:           functional.domain.create.29
# title:        CREATE DOMAIN - BLOB SEGMENT SIZE
# decription:   Domain creation based on BLOB datatype with SEGMENT SIZE specification.
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.domain.create.create_domain_29

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE DOMAIN test BLOB SEGMENT SIZE 244;
SHOW DOMAIN test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """TEST                            BLOB segment 244, subtype BINARY Nullable"""

@pytest.mark.version('>=2.0')
def test_29_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

