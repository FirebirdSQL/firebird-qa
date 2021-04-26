#coding:utf-8
#
# id:           bugs.core_881
# title:        Singleton isn't respected in COMPUTED BY expressions
# decription:   
# tracker_id:   CORE-881
# min_versions: []
# versions:     2.5.0
# qmid:         bugs.core_881-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t1 (n integer);
create table t2 (n integer, c computed by ((select n from t1)));

insert into t1 values (1);
insert into t1 values (2);
insert into t2 values (1);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select * from t2;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """N            C
============ ============
"""
expected_stderr_1 = """Statement failed, SQLSTATE = 21000
multiple rows in singleton select
"""

@pytest.mark.version('>=2.5.0')
def test_core_881_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

