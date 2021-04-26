#coding:utf-8
#
# id:           functional.domain.create.31
# title:        CREATE DOMAIN - BLOB (seglen,subtype)
# decription:   Domain creation based on BLOB datatype with seglen-subtype specification.
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.domain.create.create_domain_31

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE DOMAIN test BLOB(349,1);
SHOW DOMAIN test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """TEST                            BLOB segment 349, subtype TEXT Nullable
"""

@pytest.mark.version('>=1.0')
def test_31_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

