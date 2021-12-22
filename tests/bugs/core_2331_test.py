#coding:utf-8
#
# id:           bugs.core_2331
# title:        ALTER DOMAIN invalid RDB$FIELD_SUB_TYPE
# decription:   
# tracker_id:   CORE-2331
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE DOMAIN TESTDOM VARCHAR(50);
COMMIT;
ALTER DOMAIN TESTDOM TYPE VARCHAR(80);
COMMIT;

SELECT RDB$FIELD_SUB_TYPE FROM RDB$FIELDS WHERE RDB$FIELD_NAME = 'TESTDOM';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
RDB$FIELD_SUB_TYPE
==================
                 0

"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

