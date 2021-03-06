#coding:utf-8
#
# id:           bugs.core_4743
# title:        Granted role does not work with non-ascii username
# decription:   
#                   Test creates non-ascii user and role, and also several kind of DB objects (table, procedure, function etc).
#                   Then role is granted to user, and privileges for DB objects are granted to this role.
#                   All these actions are done in ISQL which is launched as separate (child) process.
#                   No errors must be raised in it (see 'f_ddl_log' - it must remain empty).
#               
#                   Further, we try to establish connection to the test DB using non-ascii user and role.
#               
#                   ::: NB :::
#                   Attempt to use ISQL for connect with non-ascii login will FAIL with:
#                       Statement failed, SQLSTATE = 22021
#                       Bad international character in tag isc_dpb_user_name
#                       -Cannot transliterate character between character sets
#                       -Invalid or incomplete multibyte or wide character
#               
#                   Fortunately, this can be done without problems using fdb.connect().
#               
#                   After connect, we obtain:
#                   * name of current user and his role (both of them must be non-ascii);
#                   * privileges that was granted to this user (see query to v_current_privileges);
#               
#                   Finally, we disconnect, generate SQL script for drop this user and run ISQL for this
#                   (we have to do this because it seems that there is no way to drop NON-ASCII user via FDB Services).
#               
#                   NOTE: Python package 'io' is used here instead of codecs (the latter is obsolete in Python).
#               
#                   Checked on: 4.0.0.2416 (Windows and Linux)
#                 
# tracker_id:   
# min_versions: ['4.0']
# versions:     4.0
# qmid:         bugs.core_4743

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[\t ]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import io
#  #import codecs
#  import subprocess
#  import time
#  
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
#            print('type(f_names_list[i])=',type(f_names_list[i]))
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  sql_txt='''    set bail on;
#      set names utf8;
#      connect '%(dsn)s' user '%(user_name)s' password '%(user_password)s';
#  
#      create or alter user "Вася Пупкин" password '123' using plugin Srp;
#      create role "Старший дворник";
#      commit;
#  
#      grant "Старший дворник" to "Вася Пупкин";
#      commit;
#  
#      create table "Документы"(id int primary key, pid int references "Документы");
#      create  exception "НЕ_число" 'Ваша строка не может быть преобразована в число.';
#      create sequence "ИД_документа";
#      set term ^;
#      create procedure "Хранимка" as
#      begin
#      end
#      ^
#      create function "СтрВЧисло"(a_text varchar(100)) returns int as
#      begin
#          return 0;
#      end
#      ^
#  
#      create or alter package "Утилиты" as
#      begin
#          procedure pg_sp_worker;
#      end
#      ^
#      recreate package body "Утилиты" as
#      begin
#          procedure pg_sp_worker as
#          begin
#          end
#      end
#      ^
#      set term ;^
#      commit;
#  
#      create or alter view v_current_privileges as
#      select
#           g.rdb$user as who_is_granted
#          ,g.rdb$relation_name as obj_name
#          ,decode( g.rdb$object_type
#                   ,0,'table'
#                   ,1,'view'
#                   ,2,'trigger'
#                   ,5,'procedure'
#                   ,7,'exception'
#                   ,9,'domain'
#                   ,11,'charset'
#                   ,13,'role'
#                   ,14,'generator'
#                   ,15,'function'
#                   ,16,'blob filt'
#                   ,18,'package'
#                   ,22,'systable'
#                   ,cast(g.rdb$object_type as varchar(50))
#                 ) as obj_type
#          ,max(iif(g.rdb$privilege='S','YES',' ')) as "privilege:select"
#          ,max(iif(g.rdb$privilege='I','YES',' ')) as "privilege:insert"
#          ,max(iif(g.rdb$privilege='U','YES',' ')) as "privilege:update"
#          ,max(iif(g.rdb$privilege='D','YES',' ')) as "privilege:delete"
#          ,max(iif(g.rdb$privilege='G','YES',' ')) as "privilege:usage"
#          ,max(iif(g.rdb$privilege='X','YES',' ')) as "privilege:exec"
#          ,max(iif(g.rdb$privilege='R','YES',' ')) as "privilege:refer"
#          ,max(iif(g.rdb$privilege='C','YES',' ')) as "privilege:create"
#          ,max(iif(g.rdb$privilege='L','YES',' ')) as "privilege:alter"
#          ,max(iif(g.rdb$privilege='O','YES',' ')) as "privilege:drop"
#          ,max(iif(g.rdb$privilege='M','YES',' ')) as "privilege:member"
#      from rdb$user_privileges g
#      where g.rdb$user in( current_user, current_role )
#      group by 1,2,3;
#  
#      grant select on v_current_privileges to "Старший дворник";
#      grant select,insert,update,delete,references on "Документы" to "Старший дворник";
#      grant usage on exception "НЕ_число" to "Старший дворник";
#      grant usage on sequence "ИД_документа" to "Старший дворник";
#      grant execute on procedure "Хранимка" to "Старший дворник";
#      grant execute on function "СтрВЧисло" to "Старший дворник";
#      grant execute on package "Утилиты" to "Старший дворник";
#      grant create table to "Старший дворник";
#      grant alter any table to "Старший дворник";
#      grant drop any table to "Старший дворник";
#      commit;
#  
#      /*
#          DO NOT try to use ISQL for connecti using non-ascii user name! It will fail with:
#          =====
#             Statement failed, SQLSTATE = 22021
#             Bad international character in tag isc_dpb_user_name
#             -Cannot transliterate character between character sets
#             -Invalid or incomplete multibyte or wide character
#          =====
#          XXX DOES NOT WORK XXX >>> connect '%(dsn)s' user "Вася Пупкин" password '123' role "Старший дворник";
#          Instead, FDB connect() method must be used for this.
#      */
#  ''' % dict(globals(), **locals())
#  
#  f_ddl_sql = open( os.path.join(context['temp_directory'], 'tmp_4743_utf8_ddl.sql'), 'w' )
#  f_ddl_sql.write( sql_txt )
#  flush_and_close( f_ddl_sql )
#  
#  f_ddl_log = open( os.path.splitext(f_ddl_sql.name)[0]+'.log', 'w')
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_ddl_sql.name ],
#                   stdout = f_ddl_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_ddl_log )
#  
#  with io.open(f_ddl_log.name, 'r', encoding='utf8' ) as f:
#      result_log = f.readlines()
#  
#  for i in result_log:
#      print( i.encode('utf8') ) # do not miss '.encode()' here, otherwise get: "ordinal not in range(128)"
#  
#  f_run_log = io.open( os.path.join(context['temp_directory'], 'tmp_4743_utf8_run.log'), 'w', encoding = 'utf8' )
#  
#  con = fdb.connect(dsn = dsn, user = "Вася Пупкин", password = '123', role = 'Старший дворник', charset = 'utf8', utf8params = True)
#  cur = con.cursor()
#  cur.execute('select m.mon$user,m.mon$role from mon$attachments m where m.mon$attachment_id = current_connection')
#  col = cur.description
#  for r in cur:
#      for i in range(0,len(col)):
#          f_run_log.write( ' '.join((col[i][0],':',r[i], '\\n')) )
#  
#  cur.execute('select v.* from v_current_privileges v')
#  col = cur.description
#  for r in cur:
#      for i in range(0,len(col)):
#          if 'privilege:' not in col[i][0] or 'privilege:' in col[i][0] and r[i] == 'YES':
#              f_run_log.write( ' '.join((col[i][0],':',r[i], '\\n')) )
#  
#  flush_and_close( f_run_log )
#  
#  # Check that privileges actually work for current (non-ascii) user /  role:
#  #####################################
#  # All following actions must not raise any exception:
#  
#  '''
#          ### DEFERRED ###
#          Got exception on Linux:
#              - SQLCODE: -104
#              - Dynamic SQL Error
#              - SQL error code = -104
#              - Token unknown - line 1, column 13
#              - "Документы"
#              -104
#              335544569
#  
#          con.execute_immediate('insert into "Документы"(id) values(gen_id("ИД_документа",1))')
#          cur.callproc('"Хранимка"')
#          cur.execute('select "СтрВЧисло"(?) from rdb$database', (123,))
#          for r in cur:
#              pass
#  
#          cur.callproc('"Утилиты".pg_sp_worker')
#  '''
#  
#  cur.close()
#  con.close()
#  
#  # Generate SQL script for DROP non-ascii user.
#  ##############################################
#  sql_txt='''
#      set bail on;
#      set names utf8;
#      set list on;
#      -- set echo on;
#      connect '%(dsn)s' user '%(user_name)s' password '%(user_password)s';
#      select count(*) non_ascii_user_before_drop from sec$users where sec$user_name ='Вася Пупкин';
#      drop user "Вася Пупкин" using plugin Srp;
#      commit;
#      select count(*) non_ascii_user_after_drop from sec$users where sec$user_name ='Вася Пупкин';
#  ''' % dict(globals(), **locals())
#  
#  f_drop_sql = open( os.path.join(context['temp_directory'], 'tmp_4743_utf8_drop.sql'), 'w' )
#  f_drop_sql.write(  sql_txt )
#  flush_and_close( f_drop_sql )
#  
#  f_drop_log = open( os.path.splitext(f_drop_sql.name)[0]+'.log', 'w')
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_drop_sql.name ],
#                   stdout = f_drop_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_drop_log )
#  
#  with io.open(f_run_log.name, 'r', encoding='utf8' ) as f:
#      result_in_utf8 = f.readlines()
#  
#  for i in result_in_utf8:
#      print( i.encode('utf8') )
#  
#  with open(f_drop_log.name,'r') as f:
#      for line in f:
#          print(line)
#  
#  # cleanup:
#  ###########
#  time.sleep(2)
#  
#  # DO NOT use here: cleanup( (f_ddl_sql, f_ddl_log, f_drop_sql, f_drop_log, f_run_log) ) -- 
#  # Unrecognized type of element: <closed file 'C:\\FBTESTING\\qa\\fbt-repo\\tmp\\tmp_4743_utf8_run.log', mode 'wb' at 0x0000000005A20780> - can not be treated as file.
#  # type(f_names_list[i])= <type 'instance'>Traceback (most recent call last):
#  
#  cleanup( [i.name for i in (f_ddl_sql, f_ddl_log, f_drop_sql, f_drop_log, f_run_log)] )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MON$USER : Вася Пупкин
    MON$ROLE : Старший дворник

    WHO_IS_GRANTED : Вася Пупкин
    OBJ_NAME : Старший дворник
    OBJ_TYPE : role
    privilege:member : YES

    WHO_IS_GRANTED : Старший дворник
    OBJ_NAME : SQL$TABLES
    OBJ_TYPE : systable
    privilege:create : YES
    privilege:alter : YES
    privilege:drop : YES

    WHO_IS_GRANTED : Старший дворник
    OBJ_NAME : V_CURRENT_PRIVILEGES
    OBJ_TYPE : table
    privilege:select : YES

    WHO_IS_GRANTED : Старший дворник
    OBJ_NAME : Документы
    OBJ_TYPE : table
    privilege:select : YES
    privilege:insert : YES
    privilege:update : YES
    privilege:delete : YES
    privilege:refer : YES

    WHO_IS_GRANTED : Старший дворник
    OBJ_NAME : ИД_документа
    OBJ_TYPE : generator
    privilege:usage : YES

    WHO_IS_GRANTED : Старший дворник
    OBJ_NAME : НЕ_число
    OBJ_TYPE : exception
    privilege:usage : YES

    WHO_IS_GRANTED : Старший дворник
    OBJ_NAME : СтрВЧисло
    OBJ_TYPE : function
    privilege:exec : YES

    WHO_IS_GRANTED : Старший дворник
    OBJ_NAME : Утилиты
    OBJ_TYPE : package
    privilege:exec : YES

    WHO_IS_GRANTED : Старший дворник
    OBJ_NAME : Хранимка
    OBJ_TYPE : procedure
    privilege:exec : YES

    NON_ASCII_USER_BEFORE_DROP 1
    NON_ASCII_USER_AFTER_DROP 0
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


