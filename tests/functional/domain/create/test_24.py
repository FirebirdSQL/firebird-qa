#coding:utf-8
#
# id:           functional.domain.create.24
# title:        CREATE DOMAIN - NATIONAL CHAR VARYING
# decription:   Simple domain creation based on NATIONAL CHAR VARYING datatype.
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.domain.create.create_domain_24

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE DOMAIN test NATIONAL CHAR VARYING(32765);
SHOW DOMAIN test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """TEST                            VARCHAR(32765) CHARACTER SET ISO8859_1 Nullable
"""

@pytest.mark.version('>=1.0')
def test_24_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

