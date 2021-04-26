#coding:utf-8
#
# id:           bugs.core_0104
# title:        Dropping and recreating a table in the same txn disables PK
# decription:   
# tracker_id:   CORE-104
# min_versions: []
# versions:     2.5.3
# qmid:         bugs.core_104-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """create table test (acolumn int not null primary key);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET AUTODDL OFF;

drop table test;
create table test (acolumn int not null primary key);

commit;

insert into test values (1);
insert into test values (1);

commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 23000
violation of PRIMARY or UNIQUE KEY constraint "INTEG_4" on table "TEST"
-Problematic key value is ("ACOLUMN" = 1)
"""

@pytest.mark.version('>=2.5.3')
def test_core_0104_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

