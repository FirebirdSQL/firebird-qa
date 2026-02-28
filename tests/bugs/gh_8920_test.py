#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8920
TITLE:       Can not ALTER VIEW if it was created using function in its query and name of column changed
DESCRIPTION:
NOTES:
    [28.02.2026] pzotov
    Confirmed problem on 6.0.0.1794-f0cac4e
    Checked on 6.0.0.1794-74f8ff6.
"""
import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    set list on;
    create view v_test as select row_number()over() rn from rdb$database;
    commit;
    alter view v_test as select 1 x from rdb$database;
    commit;
    select * from v_test;
"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    X 1
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
