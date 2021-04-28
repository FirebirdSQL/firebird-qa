#coding:utf-8
#
# id:           functional.database.create.10
# title:        CREATE DATABASE - Multi file DB - starting
# decription:   
#                   Database with four files. Additional files specified by STARTING AT.
#                   Checked on:
#                       2.5.9.27126: OK, 1.610s.
#                       3.0.5.33086: OK, 2.047s.
#                       4.0.0.1378: OK, 7.266s.
#                 
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     3.0, 4.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^.*TMP_CREATE_DB_10.F0', 'TMP_CREATE_DB_10.F0'), ('[ ]+', '\t')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# dsn = "".join([context["server_location"],
#                          context[db_path_property],
#                          "TMP_CREATE_DB_10.FDB"])
#  
#  file1 = "".join([context[db_path_property], "TMP_CREATE_DB_10.F00"])
#  file2 = "".join([context[db_path_property], "TMP_CREATE_DB_10.F01"])
#  file3 = "".join([context[db_path_property], "TMP_CREATE_DB_10.F02"])
#  
#  createCommand = "CREATE DATABASE '%s' USER '%s' PASSWORD '%s' FILE '%s' STARTING AT PAGE 201 FILE '%s' STARTING AT PAGE 601 FILE '%s' STARTING AT PAGE 1001" % (dsn, user_name, user_password, file1, file2, file3)
#  
#  db_conn= kdb.create_database(createCommand, int(sql_dialect))
#  
#  sql='''
#  set list on;
#  select
#      cast(rdb$file_name as varchar(60)) db_file
#      ,rdb$file_sequence
#      ,rdb$file_start
#      ,rdb$file_length
#  from rdb$files
#  ;
#  '''
#  runProgram('isql',[dsn,'-user',user_name,'-pas',user_password],sql)
#  
#  db_conn.drop_database()
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TMP_CREATE_DB_10.F00
    RDB$FILE_SEQUENCE     1
    RDB$FILE_START        201
    RDB$FILE_LENGTH       400
    TMP_CREATE_DB_10.F01
    RDB$FILE_SEQUENCE     2
    RDB$FILE_START        601
    RDB$FILE_LENGTH       400
    TMP_CREATE_DB_10.F02
    RDB$FILE_SEQUENCE     3
    RDB$FILE_START        1001
    RDB$FILE_LENGTH       0
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


# version: 4.0
# resources: None

substitutions_2 = [('^.*TMP_CREATE_DB_10.F0', 'TMP_CREATE_DB_10.F0'), ('[ ]+', '\t')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

# test_script_2
#---
# dsn = "".join([context["server_location"],
#                          context[db_path_property],
#                          "TMP_CREATE_DB_10.FDB"])
#  
#  file1 = "".join([context[db_path_property], "TMP_CREATE_DB_10.F00"])
#  file2 = "".join([context[db_path_property], "TMP_CREATE_DB_10.F01"])
#  file3 = "".join([context[db_path_property], "TMP_CREATE_DB_10.F02"])
#  
#  createCommand = "CREATE DATABASE '%s' USER '%s' PASSWORD '%s' FILE '%s' STARTING AT PAGE 301 FILE '%s' STARTING AT PAGE 801 FILE '%s' STARTING AT PAGE 1301" % (dsn, user_name, user_password, file1, file2, file3)
#  
#  db_conn= kdb.create_database(createCommand, int(sql_dialect))
#  
#  sql='''
#  set list on;
#  select
#      cast(rdb$file_name as varchar(60)) db_file
#      ,rdb$file_sequence
#      ,rdb$file_start
#      ,rdb$file_length
#  from rdb$files
#  ;
#  '''
#  runProgram('isql',[dsn,'-user',user_name,'-pas',user_password],sql)
#  
#  db_conn.drop_database()
#---
#act_2 = python_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    TMP_CREATE_DB_10.F00
    RDB$FILE_SEQUENCE     1
    RDB$FILE_START        301
    RDB$FILE_LENGTH       500
    TMP_CREATE_DB_10.F01
    RDB$FILE_SEQUENCE     2
    RDB$FILE_START        801
    RDB$FILE_LENGTH       500
    TMP_CREATE_DB_10.F02
    RDB$FILE_SEQUENCE     3
    RDB$FILE_START        1301
    RDB$FILE_LENGTH       0
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_2(db_2):
    pytest.fail("Test not IMPLEMENTED")


