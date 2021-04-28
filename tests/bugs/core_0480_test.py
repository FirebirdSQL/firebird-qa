#coding:utf-8
#
# id:           bugs.core_0480
# title:        Foreign key relation VARCHAR <-> INT
# decription:   
# tracker_id:   CORE-480
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_480-21

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """create table T1 (PK1 INTEGER, COL VARCHAR(10));
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """create table T2 (PK2 INTEGER, FK1 VARCHAR(10), COL VARCHAR(10),
foreign key (FK1) references T1 (PK1));

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE TABLE T2 failed
-could not find UNIQUE or PRIMARY KEY constraint in table T1 with specified columns
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

