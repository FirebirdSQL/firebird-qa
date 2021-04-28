#coding:utf-8
#
# id:           bugs.core_0850
# title:        DYN allows to set defaults for computed fields when altering a field
# decription:   
# tracker_id:   CORE-850
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_850

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t2(a int, b int computed by (00));
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """alter table t2 alter b set default 5;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-ALTER TABLE T2 failed
-Cannot add or remove COMPUTED from column B
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

