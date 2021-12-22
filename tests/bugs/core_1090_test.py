#coding:utf-8
#
# id:           bugs.core_1090
# title:        Error msg "Could not find UNIQUE INDEX" when in fact one is present
# decription:   
# tracker_id:   CORE-1090
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_1090-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t (i integer not null);
create unique index ti on t(i);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """show table t;
show index ti;

create table t2 (i integer references t(i));
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """I                               INTEGER Not Null
TI UNIQUE INDEX ON T(I)
"""
expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE TABLE T2 failed
-could not find UNIQUE or PRIMARY KEY constraint in table T with specified columns
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

