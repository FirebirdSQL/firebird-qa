#coding:utf-8
#
# id:           bugs.core_1156
# title:        Prepare fails when having a parameter in a DSQL statement before a sub query
# decription:   
# tracker_id:   CORE-1156
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1156

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  try:
#    c.prep('select count(*) from rdb$database where ? < (select count(*) from rdb$database)')
#  except:
#    print ('Test FAILED in case 1')
#  
#  try:
#    c.prep('select count(*) from rdb$database where (select count(*) from rdb$database) > ?')
#  except:
#    print ('Test FAILED in case 2')
#  
#  try:
#    c.prep('select count(*) from rdb$database where ? < cast ((select count(*) from rdb$database) as integer)')
#  except:
#    print ('Test FAILED in case 3')
#  
#  try:
#    c.prep('select count(*) from rdb$database where 0 < (select count(*) from rdb$database)')
#  except:
#    print ('Test FAILED in case 4')
#  
#  try:
#    c.prep('select count(*) from rdb$database where cast (? as integer) < (select count(*) from rdb$database)')
#  except:
#    print ('Test FAILED in case 5')
#  
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


