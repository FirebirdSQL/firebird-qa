#coding:utf-8
#
# id:           bugs.core_0282
# title:        DOMAINs don't register their dependency on other objects
# decription:   
# tracker_id:   CORE-282
# min_versions: []
# versions:     2.5
# qmid:         bugs.core_282-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """create table t(a int);
create domain d int check(value > (select max(a) from t));
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """drop table t;
commit;
create table u(a d);
commit;
show table u;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """A                               (D) INTEGER Nullable
                                check(value > (select max(a) from t))
"""
expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-cannot delete
-COLUMN T.A
-there are 1 dependencies
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

