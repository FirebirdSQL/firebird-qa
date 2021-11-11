#coding:utf-8
#
# id:           bugs.core_1315
# title:        Data type unknown
# decription:
# tracker_id:   CORE-1315
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1315

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# cur = db_conn.cursor()
#  try:
#    statement = cur.prep('select coalesce(?,1) from RDB$DATABASE')
#  except Exception,e:
#    print ('Failed!',e)
#  else:
#    cur.execute(statement,[2])
#    printData(cur)
#    print()
#    cur.execute(statement,[None])
#    printData(cur)
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """COALESCE
-----------
2

COALESCE
-----------
1
"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action, capsys):
    with act_1.db.connect() as con:
        c = con.cursor()
        statement = c.prepare('select coalesce(?,1) from RDB$DATABASE')
        c.execute(statement,[2])
        act_1.print_data(c)
        c.execute(statement,[None])
        act_1.print_data(c)
        act_1.stdout = capsys.readouterr().out
        act_1.expected_stdout = expected_stdout_1
        assert act_1.clean_stdout == act_1.clean_expected_stdout


