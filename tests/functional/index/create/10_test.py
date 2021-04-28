#coding:utf-8
#
# id:           functional.index.create.10
# title:        CREATE INDEX - try create index with same name
# decription:   CREATE INDEX - try create index with same name
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               INSERT
#               SHOW INDEX
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.index.create.create_index_10

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE t( a INTEGER);
CREATE INDEX test ON t(a);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE INDEX test ON t(a);"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42S11
unsuccessful metadata update
-CREATE INDEX TEST failed
-Index TEST already exists

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

