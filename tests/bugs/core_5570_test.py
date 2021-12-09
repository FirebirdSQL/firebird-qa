#coding:utf-8
#
# id:           bugs.core_5570
# title:        Negative infinity (double) shown incorrectly without sign in isql
# decription:
#                   Bug was in ISQL. We do insert in the table with two DP fields special values which
#                   are "-1.#INF" and "1.#INF" (at least in such view they are represented in the trace).
#                   These values are defined in Python class Decimal as literals '-Infinity' and 'Infinity'.
#                   After this we try to query this table. Expected result: "minus" sign should be shown
#                   leftside of negative infinity.
#
#                   Confirmed WRONG output (w/o sign with negative infinity) on 3.0.3.32756, 4.0.0.690.
#                   All fine on:
#                     3.0.3.32794: OK, 1.235s.
#                     4.0.0.713: OK, 1.203s.
#
# tracker_id:   CORE-5570
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:

import pytest
from decimal import Decimal
from firebird.qa import db_factory, python_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = []

init_script_1 = """
      recreate table test(x double precision, y double precision);
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  from decimal import *
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#
#  x1=Decimal('-Infinity')
#  y1=Decimal('Infinity')
#
#  cur1=db_conn.cursor()
#  sql='insert into test(x, y) values(?, ?)'
#
#  try:
#    cur1.execute( sql, (x1, y1, ) )
#  except Exception, e:
#    print(e[0])
#
#  cur1.close()
#  db_conn.commit()
#  db_conn.close()
#
#  runProgram('isql',[dsn], "set list on; set count on; select * from test;")
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    X                               -Infinity
    Y                               Infinity
    Records affected: 1
"""

@pytest.mark.version('>=3.0.3')
def test_1(act_1: Action):
     with act_1.db.connect() as con:
          c = con.cursor()
          c.execute('insert into test(x, y) values(?, ?)', [Decimal('-Infinity'), Decimal('Infinity')])
          con.commit()
     act_1.expected_stdout = expected_stdout_1
     act_1.isql(switches=[], input="set list on; set count on; select * from test;")
     assert act_1.clean_stdout == act_1.clean_expected_stdout
