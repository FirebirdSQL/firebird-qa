#coding:utf-8
#
# id:           bugs.core_2615
# title:        Silent truncation when using utf8 parameters and utf8 client character set encoding
# decription:   
# tracker_id:   CORE-2615
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE test (c CHAR(10) CHARACTER SET UTF8);
COMMIT;"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """INSERT INTO test VALUES ('012345679012345');
COMMIT;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 22001
arithmetic exception, numeric overflow, or string truncation
-string right truncation
-expected length 10, actual 15
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

