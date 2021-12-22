#coding:utf-8
#
# id:           bugs.core_3675
# title:        CREATE INDEX considers NULL and empty string being the same in compound indices
# decription:   
# tracker_id:   CORE-3675
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core3675.fbk', init=init_script_1)

test_script_1 = """
    show table t;
    select * from t;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
F1                              VARCHAR(1) Nullable
F2                              VARCHAR(1) Nullable
F3                              VARCHAR(1) Nullable
F4                              VARCHAR(1) Nullable
CONSTRAINT T1_UNQ:
  Unique key (F1, F2, F3, F4)
F1     F2     F3     F4
====== ====== ====== ======
a      b      c      d
a      <null> c      d
a             c      d
a      b      <null> d
a      b      <null>
a      b             <null>
a      b      <null> <null>
a      <null> <null> <null>
<null> <null> <null> <null>
"""

@pytest.mark.version('>=2.5.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

