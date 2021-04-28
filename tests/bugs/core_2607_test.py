#coding:utf-8
#
# id:           bugs.core_2607
# title:        Introducer (_charset) problems with monitoring and persistent modules
# decription:   Usage of introducer (_charset ) is problematic due to usage of different character sets in a single command. The problems are different from version to version, and may be transliteration error, malformed string or just unexpected things.
# tracker_id:   CORE-2607
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  con2 = kdb.connect(dsn=dsn,user=user_name,password=user_password)
#  c2 = con2.cursor()
#  
#  c.execute("select _dos850 '123áé456' from rdb$database")
#  c2.execute("select mon$sql_text from mon$statements s where s.mon$sql_text containing '_dos850'")
#  #printData(c2)
#  for r in c2:
#    print(r[0])
#  
#  con2.close()
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    select mon$sql_text from mon$statements s where s.mon$sql_text containing '_dos850'
    select _dos850 X'313233C3A1C3A9343536' from rdb$database
  """

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


