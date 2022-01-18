#coding:utf-8

"""
ID:          bugs.core_0010
ISSUE:       328
TITLE:       Navigation vs IS NULL vs compound index
DESCRIPTION:
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table t (f1 int, f2 int);
    create index t_idx on t (f1, f2);

    insert into t (f1, f2) values (1, 1);
    insert into t (f1, f2) values (null, 2);
    insert into t (f1, f2) values (3, 3);

    set list on;

    select *
    from t
    where f1 is null
    order by f1, f2;
"""

act = isql_act('db', test_script)

expected_stdout = """
    F1                              <null>
    F2                              2
"""

@pytest.mark.version('>=2.5')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

