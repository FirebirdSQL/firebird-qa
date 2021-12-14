#coding:utf-8
#
# id:           bugs.core_2712
# title:        Do not print "invalid request BLR" for par.cpp errors with valid BLR
# decription:
#
# tracker_id:   CORE-2712
# min_versions: ['3.0.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action
from firebird.driver import DatabaseError

# version: 3.0
# resources: None

substitutions_1 = [('table id [0-9]+ is not defined', 'table is not defined')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.close()
#  msg=''
#
#  att1 = kdb.connect(dsn=dsn)
#  cur1 = att1.cursor()
#  cur1.execute("recreate table test(x int)")
#  att1.commit()
#  cur1.execute("insert into test values(1)")
#  att1.commit()
#
#  att2 = kdb.connect(dsn=dsn)
#  cur2 = att2.cursor()
#  cur2.execute("select 1 from rdb$database")
#
#  cur1.execute("drop table test")
#  try:
#      cur2.prep("update test set x=-x")
#      att2.commit()
#  except Exception as e:
#      msg = e[0]
#      print(msg)
#
#  att1.close()
#  att2.close()
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, capsys):
    with act_1.db.connect() as att1:
        cur1 = att1.cursor()
        cur1.execute("recreate table test(x int)")
        att1.commit()
        cur1.execute("insert into test values(1)")
        att1.commit()
        with act_1.db.connect() as att2:
            cur2 = att2.cursor()
            cur2.execute("select 1 from rdb$database")

            cur1.execute("drop table test")
            with pytest.raises(DatabaseError, match='.*table id [0-9]+ is not defined.*'):
                cur2.prepare("update test set x=-x")
                att2.commit()