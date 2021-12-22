#coding:utf-8
#
# id:           functional.domain.create.19
# title:        CREATE DOMAIN - VARCHAR - ARRAY
# decription:   Array domain creation based on VARCHAR datatype.
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.domain.create.create_domain_19

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE DOMAIN test VARCHAR(32765)[40000];
SHOW DOMAIN test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """TEST                            ARRAY OF [40000]
VARCHAR(32765) Nullable"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

