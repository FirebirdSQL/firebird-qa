#coding:utf-8
#
# id:           functional.database.alter_03
# title:        Alter database: add file with name of this database or previously added files must fail
# decription:   Add same file twice must fail
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# cursor=db_conn.cursor()
#  cursor.execute("ALTER DATABASE ADD FILE '$(DATABASE_LOCATION)TEST.G00' STARTING 10000")
#  db_conn.commit()
#  try:
#    cursor=db_conn.cursor()
#    cursor.execute("ALTER DATABASE ADD FILE '$(DATABASE_LOCATION)TEST.G00' STARTING 20000")
#    db_conn.commit()
#  except kdb.DatabaseError, e:
#    print (e[0])
#  except:
#    print ("Unexpected exception",sys.exc_info()[0])
#    print ("Arguments",sys.exc_info()[1])
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
  Error while executing SQL statement:
    - SQLCODE: -607
    - unsuccessful metadata update
    - ALTER DATABASE failed
    - Cannot add file with the same name as the database or added files
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_alter_03_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


