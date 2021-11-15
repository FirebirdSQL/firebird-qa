#coding:utf-8
#
# id:           bugs.core_2230
# title:        Implement domain check of input parameters of execute block
# decription:
# tracker_id:   CORE-2230
# min_versions: []
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action
from firebird.driver import DatabaseError

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE DOMAIN DOM1 AS INTEGER NOT NULL CHECK (value in (0, 1));
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  cmd = c.prep('execute block (x DOM1 = ?) returns (y integer) as begin y = x; suspend; end')
#
#  c.execute(cmd,[1])
#  printData(c)
#
#  try:
#    c.execute(cmd,[10])
#    printData(c)
#  except kdb.DatabaseError,e:
#    print (e[0])
#  else:
#    print ('Test Failed')
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """Y
-----------
1
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, capsys):
    with act_1.db.connect() as con:
        c = con.cursor()
        cmd = c.prepare('execute block (x DOM1 = ?) returns (y integer) as begin y = x; suspend; end')
        c.execute(cmd, [1])
        act_1.print_data(c)
        act_1.expected_stdout = expected_stdout_1
        act_1.stdout = capsys.readouterr().out
        assert act_1.clean_stdout == act_1.clean_expected_stdout
        with pytest.raises(Exception, match='.*validation error for variable X, value "10"'):
            c.execute(cmd, [10])
            act_1.print_data(c)
