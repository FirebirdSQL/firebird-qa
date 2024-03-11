#coding:utf-8

"""
ID:          issue-8033
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8033
TITLE:       Invalid result when string compared with indexed numeric(x,y) field where x > 18 and y != 0
NOTES:
    [11.03.2024] pzotov.
    Confirmed bug in 6.0.0.276.
    Checked 6.0.0.278 -- all fine.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    recreate table mi8 (v numeric (30, 4));
    insert into mi8 values(12.345);
    commit;
    create index i8 on mi8(v);
    set count on;
    select v as v1 from mi8 where v = 12.345;
    select v as v2 from mi8 where v = '12.345';
"""

act = isql_act('db', test_script, substitutions = [('[ \t]+', ' ')])

expected_stdout = """
    V1 12.3450
    Records affected: 1

    V2 12.3450
    Records affected: 1
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
