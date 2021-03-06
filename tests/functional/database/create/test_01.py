#coding:utf-8
#
# id:           functional.database.create.01
# title:        
#                   Check ability to specify SET NAMES and DEFAULT CHARACTER SET within one statement.
#                   Checked on:
#                       4.0.0.1740 SS: 1.157s.
#                       3.0.6.33236 SS: 0.808s.
#                       2.5.9.27149 SC: 0.508s.
#                   NOTE: name of client charset must be enclosed in apostrophes, i.e.: create database ... set names 'win1251' ...
#                 
# decription:   
# tracker_id:   
# min_versions: ['2.5']
# versions:     2.5.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import fdb
#  
#  
#  test_db="".join([context[db_path_property], "tmp_create_db_01.fdb"])
#  if os.path.isfile(test_db):
#      os.remove(test_db)
#  
#  db_conn.close()
#  
#  sql_ddl = "create database 'localhost:%(test_db)s' user '%(user_name)s' password '%(user_password)s' set names 'win1251' default character set utf8"  % dict(globals(), **locals())
#  
#  con = fdb.create_database( sql_ddl )
#  
#  cur = con.cursor()
#  sql='''
#      select c.rdb$character_set_name as client_char_set, r.rdb$character_set_name as db_char_set
#      from mon$attachments a join rdb$character_sets c on a.mon$character_set_id = c.rdb$character_set_id
#      cross join rdb$database r
#      where a.mon$attachment_id = current_connection
#  '''
#  
#  cur.execute(sql);
#  
#  hdr=cur.description
#  for r in cur:
#      for i in range(0,len(hdr)):
#          print( hdr[i][0],':', r[i] )
#  
#  con.commit()
#  con.drop_database()
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CLIENT_CHAR_SET : WIN1251
    DB_CHAR_SET : UTF8
  """

@pytest.mark.version('>=2.5.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


