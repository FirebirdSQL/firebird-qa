#coding:utf-8
#
# id:           bugs.core_1058
# title:        ALTER DOMAIN and ALTER TABLE don't allow to change character set and/or collation
# decription:   
# tracker_id:   CORE-1058
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1058

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE DOMAIN D_TEST AS VARCHAR(100) CHARACTER SET WIN1251;
COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ALTER DOMAIN D_TEST TYPE VARCHAR(100) CHARACTER SET UTF8;
COMMIT;
SHOW DOMAIN D_TEST;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """D_TEST                          VARCHAR(100) CHARACTER SET UTF8 Nullable
"""

@pytest.mark.version('>=2.1')
def test_core_1058_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

