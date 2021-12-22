#coding:utf-8
#
# id:           functional.database.create.09
# title:        CREATE DATABASE - Multi file DB
# decription:
#                   Create database with four files.
#                   Checked on:
#                       2.5.9.27126: OK, 0.875s.
#                       3.0.5.33086: OK, 5.797s.
#                       4.0.0.1378: OK, 8.468s.
#
# tracker_id:
# min_versions: ['2.5']
# versions:     2.5.0, 4.0
# qmid:

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = [('^.*TMP_CREATE_DB_09.F0', 'TMP_CREATE_DB_09.F0'), ('[ ]+', '\t')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1, do_not_create=True)

# test_script_1
#---
# dsn = "".join([context["server_location"],
#                          context[db_path_property],
#                          "TMP_CREATE_DB_09.FDB"])
#
#  file1 = "".join([context[db_path_property], "TMP_CREATE_DB_09.F00"])
#  file2 = "".join([context[db_path_property], "TMP_CREATE_DB_09.F01"])
#  file3 = "".join([context[db_path_property], "TMP_CREATE_DB_09.F02"])
#
#  createCommand = "CREATE DATABASE '%s' LENGTH 200 USER '%s' PASSWORD '%s' FILE '%s' LENGTH 200 FILE '%s' LENGTH 200 FILE '%s' LENGTH 200" % (dsn, user_name, user_password, file1, file2, file3)
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

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    TMP_CREATE_DB_09.F00
    RDB$FILE_SEQUENCE     1
    RDB$FILE_START        201
    RDB$FILE_LENGTH       200
    TMP_CREATE_DB_09.F01
    RDB$FILE_SEQUENCE     2
    RDB$FILE_START        401
    RDB$FILE_LENGTH       200
    TMP_CREATE_DB_09.F02
    RDB$FILE_SEQUENCE     3
    RDB$FILE_START        601
    RDB$FILE_LENGTH       200
"""

@pytest.mark.version('>=2.5.0,<4.0')
def test_1(act_1: Action):
    script = f"""
    create database '{act_1.db.dsn}' user '{act_1.db.user}'
      password '{act_1.db.password}' LENGTH 200
      FILE '{act_1.db.db_path.with_name('TMP_CREATE_DB_09.F00')}' LENGTH 200
      FILE '{act_1.db.db_path.with_name('TMP_CREATE_DB_09.F01')}' LENGTH 200
      FILE '{act_1.db.db_path.with_name('TMP_CREATE_DB_09.F02')}' LENGTH 200
    ;
    set list on ;
    select
        cast(rdb$file_name as varchar(100)) db_file
        ,rdb$file_sequence
        ,rdb$file_start
        ,rdb$file_length
    from rdb$files ;
    """
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=[], input=script, connect_db=False)
    assert act_1.clean_stdout == act_1.clean_expected_stdout


# version: 4.0
# resources: None

substitutions_2 = [('^.*TMP_CREATE_DB_09.F0', 'TMP_CREATE_DB_09.F0'), ('[ ]+', '\t')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2, do_not_create=True)

# test_script_2
#---
# dsn = "".join([context["server_location"],
#                          context[db_path_property],
#                          "TMP_CREATE_DB_09.FDB"])
#
#  DB_FILE1 = "".join([context[db_path_property], "TMP_CREATE_DB_09.F00"])
#  DB_FILE2 = "".join([context[db_path_property], "TMP_CREATE_DB_09.F01"])
#  DB_FILE3 = "".join([context[db_path_property], "TMP_CREATE_DB_09.F02"])
#
#  DB_USER=user_name
#  DB_PSWD=user_password
#  DB_FILE_LEN=300
#
#  createCommand = "CREATE DATABASE '%s' LENGTH 300 USER '%s' PASSWORD '%s' FILE '%s' LENGTH 300 FILE '%s' LENGTH 300 FILE '%s' LENGTH 300" % (dsn, user_name, user_password, DB_FILE1, DB_FILE2, DB_FILE3 )
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

act_2 = python_act('db_2', substitutions=substitutions_2)

expected_stdout_2 = """
    TMP_CREATE_DB_09.F00
    RDB$FILE_SEQUENCE     1
    RDB$FILE_START        301
    RDB$FILE_LENGTH       300
    TMP_CREATE_DB_09.F01
    RDB$FILE_SEQUENCE     2
    RDB$FILE_START        601
    RDB$FILE_LENGTH       300
    TMP_CREATE_DB_09.F02
    RDB$FILE_SEQUENCE     3
    RDB$FILE_START        901
    RDB$FILE_LENGTH       300
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    script = f"""
    create database '{act_2.db.dsn}' user '{act_2.db.user}'
      password '{act_2.db.password}' LENGTH 300
      FILE '{act_2.db.db_path.with_name('TMP_CREATE_DB_09.F00')}' LENGTH 300
      FILE '{act_2.db.db_path.with_name('TMP_CREATE_DB_09.F01')}' LENGTH 300
      FILE '{act_2.db.db_path.with_name('TMP_CREATE_DB_09.F02')}' LENGTH 300
    ;
    set list on ;
    select
        cast(rdb$file_name as varchar(100)) db_file
        ,rdb$file_sequence
        ,rdb$file_start
        ,rdb$file_length
    from rdb$files ;
    """
    act_2.expected_stdout = expected_stdout_2
    act_2.isql(switches=[], input=script, connect_db=False)
    assert act_2.clean_stdout == act_2.clean_expected_stdout
