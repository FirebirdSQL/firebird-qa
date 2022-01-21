#coding:utf-8
#
# id:           bugs.core_2230
# title:        Implement domain check of input parameters of execute block
# decription:
# tracker_id:   CORE-2230
# min_versions: []
# versions:     3.0
# qmid:         None

"""
ID:          issue-2658
ISSUE:       2658
TITLE:       Implement domain check of input parameters of execute block
DESCRIPTION:
JIRA:        CORE-2230
"""

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError

init_script = """CREATE DOMAIN DOM1 AS INTEGER NOT NULL CHECK (value in (0, 1));
"""

db = db_factory(init=init_script)

act = python_act('db')

expected_stdout = """Y
-----------
1
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):
    with act.db.connect() as con:
        c = con.cursor()
        cmd = c.prepare('execute block (x DOM1 = ?) returns (y integer) as begin y = x; suspend; end')
        c.execute(cmd, [1])
        act.print_data(c)
        act.expected_stdout = expected_stdout
        act.stdout = capsys.readouterr().out
        assert act.clean_stdout == act.clean_expected_stdout
        with pytest.raises(Exception, match='.*validation error for variable X, value "10"'):
            c.execute(cmd, [10])
            act.print_data(c)
