#coding:utf-8
#
# id:           bugs.core_2430
# title:        Server adds "NOT" at the end of default value for the TIMESTAMP field
# decription:   
# tracker_id:   CORE-2430
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

test_script_1 = """CREATE TABLE T1 (
    F1 BIGINT NOT NULL,
    F2 BIGINT NOT NULL,
    F3 TIMESTAMP DEFAULT current_timestamp NOT NULL
);

ALTER TABLE T1 ADD CONSTRAINT PK_T1 PRIMARY KEY (F1, F2);

show table t1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """F1                              BIGINT Not Null
F2                              BIGINT Not Null
F3                              TIMESTAMP Not Null DEFAULT current_timestamp
CONSTRAINT PK_T1:
  Primary key (F1, F2)
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

