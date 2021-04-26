#coding:utf-8
#
# id:           bugs.core_1926
# title:        MON$DATABASE returns outdated transaction counters
# decription:   Fields MON$NEXT_TRANSACTION etc contain incorrect (outdated) numbers on Classic if there are other active attachments.
# tracker_id:   CORE-1926
# min_versions: []
# versions:     2.1.2
# qmid:         bugs.core_1926

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  c.execute('SELECT 1 FROM RDB$DATABASE')
#  con_detail = kdb.connect(dsn=dsn.encode(),user=user_name.encode(),password=user_password.encode())
#  con_detail.begin()
#  c = con_detail.cursor()
#  c.execute("select MON$NEXT_TRANSACTION from MON$DATABASE")
#  for row in c:
#   i = row[0]
#  con_detail.commit()
#  c.execute("select MON$NEXT_TRANSACTION from MON$DATABASE")
#  for row in c:
#   j = row[0]
#  print (j-i)
#  con_detail.commit()
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """1
"""

@pytest.mark.version('>=2.1.2')
@pytest.mark.xfail
def test_core_1926_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


