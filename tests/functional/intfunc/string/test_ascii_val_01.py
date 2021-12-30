#coding:utf-8
#
# id:           functional.intfunc.string.ascii_val_01
# title:        New Built-in Functions, Firebird 2.1 : ASCII_VAL( <string> )
# decription:   test of ASCII_VAL
#               
#               Returns the ASCII code of the first character of the specified string.
#               
#                  1.
#               
#                     Returns 0 if the string is empty
#                  2.
#               
#                     Throws an error if the first character is multi-byte
#               
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.string.ascii_val_01

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  try:
#    c.execute("select ascii_val( 'A' ) from rdb$database")
#    print (c.fetchall())
#  except Exception,e:
#    print ("Test Failed for ascii_val( 'A' )")
#    print (e)
#  else:
#    pass
#  try:
#    c.execute("select ascii_val( 'Ã' ) from rdb$database")
#    print (c.fetchall())
#  except:
#    pass
#  else:
#    print ("Test Failed for ascii_val( 'Ã' )")
#  try:
#    c.execute("select ascii_val(cast('A' as BLOB)) from rdb$database")
#    print (c.fetchall())
#  except Exception,e:
#    print ("Test Failed for ascii_val(CAST('A' AS BLOB))")
#    print (e)
#  else:
#    pass
#  try:
#    c.execute("select ascii_val(NULL) from rdb$database")
#    print (c.fetchall())
#  except Exception,e:
#    print ("Test Failed for ascii_val(NULL)")
#    print (e)
#  else:
#    pass
#  try:
#    c.execute("select ascii_val('') from rdb$database")
#    print (c.fetchall())
#  except Exception,e:
#    print ("Test Failed for ascii_val('')")
#    print (e)
#  else:
#  pass
#---
act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """[(65,)]
[(65,)]
[(None,)]
[(0,)]"""

@pytest.mark.version('>=2.1')
@pytest.mark.xfail
def test_1(act_1: Action):
    pytest.fail("Test not IMPLEMENTED")


