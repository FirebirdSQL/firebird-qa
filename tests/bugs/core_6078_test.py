#coding:utf-8
#
# id:           bugs.core_6078
# title:        Permissions for create or alter statements are not checked
# decription:
#                   The problem occured for all kind of DB objects which allow 'create OR ALTER' statement to be applied against themselves.
#                   Test creates non-privileged user and checks for all such objects that this user can NOT create any object because missing
#                   privilege to do this.
#                   Confirmed bug on 3.0.5.33140 and 4.0.0.1532.
#
#
#                   Refactored 20.01.2020:
#                   1. Changed code in order to make its code more flexible because 3.0 and 4.0 have significant differences in stdout/stderr.
#                      Common SQL code was stored in fbt-repo
#               iles\\core_6078.sql with embedding there variable name: '%(dsn)s' -- it is known from here.
#                      Content of this file is stored in variable 'sql_text' and this variable is changed using common Python rule for substitutions:
#                          sql_text % dict(globals(), **locals()
#                      Then we save this variable to temporarily .sql script and run it.
#                   2. Added check for other kinds of DB objects: users, database, domain, table, column of table, charset and local/global mappings.
#
#                   Checked on:
#                       4.0.0.1748 SS: 2.346s.
#                       3.0.6.33236 SS: 1.898s.
#
# tracker_id:   CORE-6078
# min_versions: ['3.0.5']
# versions:     3.0.5, 4.0
# qmid:         None

import pytest
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, user_factory, User

user_0_1 = user_factory('db_1', name='tmp$c6078_0', password='123')
user_1_1 = user_factory('db_1', name='tmp$c6078_1', password='123')
user_2_1 = user_factory('db_1', name='tmp$c6078_2', password='456')

# version: 3.0.5
# resources: None

substitutions_1 = [('.*After line \\d+.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import sys
#  import time
#  import subprocess
#  from fdb import services
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  this_db = db_conn.database_name
#  db_conn.close()
#
#  #--------------------------------------------
#
#  def flush_and_close( file_handle ):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f,
#      # first do f.flush(), and
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb') and file_handle.name != os.devnull:
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#
#  #--------------------------------------------
#
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if type(f_names_list[i]) == file:
#            del_name = f_names_list[i].name
#         elif type(f_names_list[i]) == str:
#            del_name = f_names_list[i]
#         else:
#            print('Unrecognized type of element:', f_names_list[i], ' - can not be treated as file.')
#            del_name = None
#
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#
#  #--------------------------------------------
#
#  f_sql=open(os.path.join(context['files_location'],'core_6078.sql'),'r')
#  sql_text = f_sql.read()
#  flush_and_close( f_sql )
#
#  f_sql_chk = open( os.path.join(context['temp_directory'],'tmp_core_6078.sql'), 'w', buffering = 0)
#  f_sql_chk.write( sql_text % dict(globals(), **locals()) )
#  flush_and_close( f_sql_chk )
#
#  f_sql_log = open( '.'.join( (os.path.splitext( f_sql_chk.name )[0], 'log') ), 'w', buffering = 0)
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_sql_chk.name ], stdout = f_sql_log, stderr = subprocess.STDOUT)
#  flush_and_close( f_sql_log )
#
#  with open( f_sql_log.name,'r') as f:
#      for line in f:
#          if line.strip():
#              print( line )
#
#  # cleanup
#  #########
#  time.sleep(1)
#  cleanup( (f_sql_log, f_sql_chk) )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    Statement failed, SQLSTATE = 28000
    modify record error
    -no permission for UPDATE access to COLUMN PLG$SRP_VIEW.PLG$ACTIVE

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER DATABASE failed
    -no permission for ALTER access to DATABASE

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER DOMAIN DM_TEST failed
    -no permission for ALTER access to DOMAIN DM_TEST

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER TABLE TEST failed
    -no permission for ALTER access to TABLE TEST

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER TABLE TEST failed
    -no permission for ALTER access to TABLE TEST

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER INDEX TEST_UID failed
    -no permission for ALTER access to TABLE TEST

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -COMMENT ON TEST failed
    -no permission for ALTER access to TABLE TEST

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -CREATE OR ALTER TRIGGER TEST_BI failed
    -no permission for ALTER access to TABLE TEST

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -CREATE OR ALTER TRIGGER TRG$START failed
    -no permission for ALTER access to DATABASE

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -CREATE OR ALTER TRIGGER TRIG_DDL_SP failed
    -no permission for ALTER access to DATABASE


    ALTERED_TRIGGER_NAME            TEST_BI
    ALTERED_TRIGGER_SOURCE          c:3d0
    as
        begin
           new.uid = gen_uuid();
        end


    Records affected: 1
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER PACKAGE PKG_TEST failed
    -There is no privilege for this operation

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -RECREATE PACKAGE BODY PKG_TEST failed
    -There is no privilege for this operation


    ALTERED_PKG_NAME                <null>


    Records affected: 1
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER FUNCTION FN_C6078 failed
    -There is no privilege for this operation


    ALTERED_STANDALONE_FUNC         <null>


    Records affected: 1
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER PROCEDURE SP_C6078 failed
    -There is no privilege for this operation


    ALTERED_STANDALONE_PROC         <null>


    Records affected: 1
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER VIEW V_C6078 failed
    -There is no privilege for this operation


    ALTERED_VIEW_NAME               <null>


    Records affected: 1
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER SEQUENCE SQ_C6078 failed
    -There is no privilege for this operation


    ALTERED_SEQUENCE_NAME           <null>


    Records affected: 1
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER EXCEPTION EX_C6078 failed
    -There is no privilege for this operation


    ALTERED_EXCEPTION_NAME          <null>


    Records affected: 1
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER FUNCTION WAIT_EVENT failed
    -There is no privilege for this operation


    ALTERED_UDR_BASED_FUNC          <null>


    Records affected: 1
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER CHARACTER SET UTF8 failed
    -no permission for ALTER access to CHARACTER SET UTF8

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER MAPPING LOCAL_MAP_C6078 failed
    -Unable to perform operation.  You must be either SYSDBA or owner of the database

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER MAPPING GLOBAL_MAP_C6078 failed
    -Unable to perform operation.  You must be either SYSDBA or owner of the database
"""

@pytest.mark.version('>=3.0.5,<4')
def test_1(act_1: Action, user_0_1: User, user_1_1: User, user_2_1: User):
    script_vars = {'dsn': act_1.db.dsn,
                   'user_name': act_1.db.user,
                   'user_password': act_1.db.password,}
    script_file = act_1.files_dir / 'core_6078.sql'
    script = script_file.read_text() % script_vars
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=['-q'], input=script, combine_output=True)
    assert act_1.clean_stdout == act_1.clean_expected_stdout


# version: 4.0
# resources: None

substitutions_2 = [('.*After line \\d+.*', '')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

# test_script_2
#---
#
#  import os
#  import sys
#  import time
#  import subprocess
#  from fdb import services
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  this_db = db_conn.database_name
#  db_conn.close()
#
#  #--------------------------------------------
#
#  def flush_and_close( file_handle ):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f,
#      # first do f.flush(), and
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb') and file_handle.name != os.devnull:
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#
#  #--------------------------------------------
#
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if type(f_names_list[i]) == file:
#            del_name = f_names_list[i].name
#         elif type(f_names_list[i]) == str:
#            del_name = f_names_list[i]
#         else:
#            print('Unrecognized type of element:', f_names_list[i], ' - can not be treated as file.')
#            del_name = None
#
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#
#  #--------------------------------------------
#
#  f_sql=open(os.path.join(context['files_location'],'core_6078.sql'),'r')
#  sql_text = f_sql.read()
#  flush_and_close( f_sql )
#
#  f_sql_chk = open( os.path.join(context['temp_directory'],'tmp_core_6078.sql'), 'w', buffering = 0)
#  f_sql_chk.write( sql_text % dict(globals(), **locals()) )
#  flush_and_close( f_sql_chk )
#
#
#  f_sql_log = open( '.'.join( (os.path.splitext( f_sql_chk.name )[0], 'log') ), 'w', buffering = 0)
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_sql_chk.name ], stdout = f_sql_log, stderr = subprocess.STDOUT)
#  flush_and_close( f_sql_log )
#
#  with open( f_sql_log.name,'r') as f:
#      for line in f:
#          if line.strip():
#              print( line )
#
#  # cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (f_sql_log, f_sql_chk) )
#
#
#
#---

act_2 = python_act('db_2', substitutions=substitutions_2)

user_0_2 = user_factory('db_2', name='tmp$c6078_0', password='123')
user_1_2 = user_factory('db_2', name='tmp$c6078_1', password='123')
user_2_2 = user_factory('db_2', name='tmp$c6078_2', password='456')

expected_stdout_2 = """
    Statement failed, SQLSTATE = 28000
    modify record error
    -no permission for UPDATE access to COLUMN PLG$SRP_VIEW.PLG$ACTIVE
    -Effective user is TMP$C6078_0

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER DATABASE failed
    -no permission for ALTER access to DATABASE

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER DOMAIN DM_TEST failed
    -no permission for ALTER access to DOMAIN DM_TEST
    -Effective user is TMP$C6078_0

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER TABLE TEST failed
    -no permission for ALTER access to TABLE TEST
    -Effective user is TMP$C6078_0

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER TABLE TEST failed
    -no permission for ALTER access to TABLE TEST
    -Effective user is TMP$C6078_0

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER INDEX TEST_UID failed
    -no permission for ALTER access to TABLE TEST
    -Effective user is TMP$C6078_0

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -COMMENT ON TEST failed
    -no permission for ALTER access to TABLE TEST
    -Effective user is TMP$C6078_0

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -CREATE OR ALTER TRIGGER TEST_BI failed
    -no permission for ALTER access to TABLE TEST
    -Effective user is TMP$C6078_0

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -CREATE OR ALTER TRIGGER TRG$START failed
    -no permission for ALTER access to DATABASE

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -CREATE OR ALTER TRIGGER TRIG_DDL_SP failed
    -no permission for ALTER access to DATABASE


    ALTERED_TRIGGER_NAME            TEST_BI
    ALTERED_TRIGGER_SOURCE          c:3cc
    as
        begin
           new.uid = gen_uuid();
        end


    Records affected: 1
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER PACKAGE PKG_TEST failed
    -No permission for CREATE PACKAGE operation

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -RECREATE PACKAGE BODY PKG_TEST failed
    -No permission for CREATE PACKAGE operation


    ALTERED_PKG_NAME                <null>


    Records affected: 1
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER FUNCTION FN_C6078 failed
    -No permission for CREATE FUNCTION operation

    ALTERED_STANDALONE_FUNC         <null>


    Records affected: 1
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER PROCEDURE SP_C6078 failed
    -No permission for CREATE PROCEDURE operation

    ALTERED_STANDALONE_PROC         <null>


    Records affected: 1
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER VIEW V_C6078 failed
    -No permission for CREATE VIEW operation

    ALTERED_VIEW_NAME               <null>


    Records affected: 1
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER SEQUENCE SQ_C6078 failed
    -No permission for CREATE GENERATOR operation

    ALTERED_SEQUENCE_NAME           <null>


    Records affected: 1
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER EXCEPTION EX_C6078 failed
    -No permission for CREATE EXCEPTION operation

    ALTERED_EXCEPTION_NAME          <null>


    Records affected: 1
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER FUNCTION WAIT_EVENT failed
    -No permission for CREATE FUNCTION operation

    ALTERED_UDR_BASED_FUNC          <null>


    Records affected: 1
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER CHARACTER SET UTF8 failed
    -no permission for ALTER access to CHARACTER SET UTF8
    -Effective user is TMP$C6078_0

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER MAPPING LOCAL_MAP_C6078 failed
    -Unable to perform operation
    -System privilege CHANGE_MAPPING_RULES is missing

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER MAPPING GLOBAL_MAP_C6078 failed
    -Unable to perform operation
    -System privilege CHANGE_MAPPING_RULES is missing
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action, user_0_2: User, user_1_2: User, user_2_2: User):
    script_vars = {'dsn': act_2.db.dsn,
                   'user_name': act_2.db.user,
                   'user_password': act_2.db.password,}
    script_file = act_2.files_dir / 'core_6078.sql'
    script = script_file.read_text() % script_vars
    act_2.expected_stdout = expected_stdout_2
    act_2.isql(switches=['-q'], input=script, combine_output=True)
    assert act_2.clean_stdout == act_2.clean_expected_stdout

