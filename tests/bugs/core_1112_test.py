#coding:utf-8
#
# id:           bugs.core_1112
# title:        Crash when dealing with a string literal longer than 32K
# decription:   This test may crash the server
# tracker_id:   CORE-1112
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1112

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  longstr = 'abc' * 10930
#  try:
#    c.execute("select * from rdb$database where '%s' = 'a'" % longstr)
#  except:
#    pass
#
#  try:
#    c.execute("select * from rdb$database where '%s' containing 'a'" % longstr)
#  except:
#    pass
#  c.execute("select 'a' from rdb$database")
#  print (c.fetchall())
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    with act_1.db.connect() as con:
        c = con.cursor()
        longstr = 'abc' * 10930
        c.execute(f"select * from rdb$database where '{longstr}' = 'a'")
        c.execute(f"select * from rdb$database where '{longstr}' containing 'a'")
        c.execute("select 'a' from rdb$database")
        result = c.fetchall()
        assert result == [('a',)]


