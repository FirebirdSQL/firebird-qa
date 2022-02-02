#coding:utf-8

"""
ID:          issue-3109
ISSUE:       3109
TITLE:       Do not print "invalid request BLR" for par.cpp errors with valid BLR
DESCRIPTION:
JIRA:        CORE-2712
FBTEST:      bugs.core_2712
"""

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError

db = db_factory()

act = python_act('db', substitutions=[('table id [0-9]+ is not defined', 'table is not defined')])

@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):
    with act.db.connect() as att1:
        cur1 = att1.cursor()
        cur1.execute("recreate table test(x int)")
        att1.commit()
        cur1.execute("insert into test values(1)")
        att1.commit()
        with act.db.connect() as att2:
            cur2 = att2.cursor()
            cur2.execute("select 1 from rdb$database")

            cur1.execute("drop table test")
            with pytest.raises(DatabaseError, match='.*table id [0-9]+ is not defined.*'):
                cur2.prepare("update test set x=-x")
                att2.commit()
