#coding:utf-8

"""
ID:          issue-4025
ISSUE:       4025
TITLE:       CREATE INDEX considers NULL and empty string being the same in compound indices
DESCRIPTION:
JIRA:        CORE-3675
FBTEST:      bugs.core_3675
"""

import pytest
from firebird.qa import *

db = db_factory(from_backup='core3675.fbk')

test_script = """
    show table t;
    select * from t;
"""

act = isql_act('db', test_script)

expected_stdout = """
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

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

