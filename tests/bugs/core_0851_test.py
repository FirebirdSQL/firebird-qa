#coding:utf-8
#
# id:           bugs.core_0851
# title:        Field can be used multiple times in multi-segment index definition
# decription:   
# tracker_id:   CORE-851
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_851-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t (i integer);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """create index ti on t(i,i);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE INDEX TI failed
-Field I cannot be used twice in index TI
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

