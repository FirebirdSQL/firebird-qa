#coding:utf-8
#
# id:           bugs.core_1559
# title:        Dropping NOT NULL contranint doesn'have the desired effect
# decription:   
# tracker_id:   CORE-1559
# min_versions: []
# versions:     2.5.3
# qmid:         bugs.core_1559-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """create table t (n integer constraint c not null);
COMMIT;
insert into t values (null);
COMMIT;
alter table t drop constraint c;
COMMIT;
insert into t values (null);
COMMIT;
SELECT * FROM t;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\Users\\win7\\Firebird_tests\\fbt-repository\\tmp\\bugs.core_1559.fdb, User: SYSDBA
SQL> SQL> SQL> SQL> SQL> SQL> SQL> SQL> SQL>
           N
============
      <null>

SQL>"""
expected_stderr_1 = """Statement failed, SQLSTATE = 23000
validation error for column "T"."N", value "*** null ***"
"""

@pytest.mark.version('>=2.5.3')
def test_core_1559_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

