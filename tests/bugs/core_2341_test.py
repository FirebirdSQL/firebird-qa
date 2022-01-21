#coding:utf-8

"""
ID:          issue-2765
ISSUE:       2765
TITLE:       Hidden variables conflict with output parameters, causing assertions, unexpected errors or possibly incorrect results
DESCRIPTION:
JIRA:        CORE-2341
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stdout = """O
----------
asd
"""

@pytest.mark.version('>=3')
def test_1(act: Action, capsys):
    with act.db.connect() as con:
        c = con.cursor()
        cmd = c.prepare("""execute block (i varchar(10) = ?) returns (o varchar(10))
        as
        begin
          o = coalesce(cast(o as date), current_date);
          o = i;
          suspend;
        end""")
        c.execute(cmd, ['asd'])
        act.print_data(c)
        #
        act.expected_stdout = expected_stdout
        act.stdout = capsys.readouterr().out
        assert act.clean_stdout == act.clean_expected_stdout
