#coding:utf-8
#
# id:           bugs.core_5972
# title:        External engine trigger crashing server if table have computed field
# decription:   
#                   We use supplied UDR example which operates with TRIGGER for replication purpuses.
#                   Two databases are used here: one is 'main' (which is created by fbtest) and second
#                   is auxiliary and serves as slave (replica).
#               
#                   We create table PERSONS in both databases, its DDL is taken from examples code.
#                   This table will be normally replicated until we add COMPUTED BY field to it.
#               
#                   When such field is added and we issue INSERT command, standard exception must raise:
#                       Statement failed, SQLSTATE = 42000
#                       Execute statement error at isc_dsql_prepare :
#                       335544569 : Dynamic SQL Error
#                       335544436 : SQL error code = -206
#                       335544578 : Column unknown
#                       335544382 : COMP
#                       336397208 : At line 1, column 57
#                       Statement : insert into "PERSONS" ("ID", "NAME", "ADDRESS", "INFO", "COMP") values (?, ?, ?, ?, ?)
#                       Data source : Firebird::C:\\FBTESTING\\qa\\misc	mprepl.fdb
#                       -At block line: ...
#                       -At trigger 'PERSONS_REPLICATE'
#               
#                   We expect appearing of this exception (see try/except block): check its class and content of message.
#               
#                   Confirmed crash on 4.0.0.1346 (built 17-dec-2018).
#                   Checked on 4.0.0.1391 (built 22-jan-2019): all fine, got expected exception.
#                   Cheked also on:
#                       4.0.0.1803 SS: 2.494s.
#                       4.0.0.1796 CS: 3.500s.
#                       3.0.6.33265 SS: 1.578s.
#                       3.0.6.33247 CS: 2.032s.
# tracker_id:   CORE-5972
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = [('[ \t]+', ' '), ('.* At block line.*', 'At block'), ('read-only column.*', 'read-only column'), ('Statement.*', 'Statement'), ('Data source.*', 'Data source'), ('.* At trigger.*', 'At trigger')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import time
#  import subprocess
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  this_db = db_conn.database_name
#  fb_major=db_conn.engine_version
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
#  table_ddl='''
#      create table persons (
#          id integer not null,
#          name varchar(60) not null,
#          address varchar(60),
#          info blob sub_type text,
#          comp int computed by (1) -- COMPUTED_BY FIELD AS IT IS DESCRIBED IN THE TICKET
#      );
#  '''
#  
#  fdb_repl = os.path.join(context['temp_directory'],'tmp_5972_repl.fdb')
#  cleanup( (fdb_repl,) )
#  
#  con_repl = fdb.create_database(  dsn = 'localhost:%(fdb_repl)s' % locals() )
#  con_repl.execute_immediate( table_ddl )
#  con_repl.commit()
#  con_repl.close()
#  
#  
#  db_conn.execute_immediate( table_ddl )
#  db_conn.commit()
#  
#  ddl_for_replication='''
#      create table replicate_config (
#          name varchar(31) not null,
#          data_source varchar(255) not null
#      );
#  
#      insert into replicate_config (name, data_source)
#         values ('ds1', '%(fdb_repl)s');
#  
#      create trigger persons_replicate
#          after insert on persons
#          external name 'udrcpp_example!replicate!ds1'
#          engine udr;
#  
#      create trigger persons_replicate2
#          after insert on persons
#          external name 'udrcpp_example!replicate_persons!ds1'
#          engine udr;
#      commit;
#  
#  ''' % locals()
#  
#  f_apply_ddl_sql = open( os.path.join(context['temp_directory'],'tmp_5972.sql'), 'w', buffering = 0)
#  f_apply_ddl_sql.write( ddl_for_replication )
#  flush_and_close( f_apply_ddl_sql )
#  
#  f_apply_ddl_log = open( '.'.join( (os.path.splitext( f_apply_ddl_sql.name )[0], 'log') ), 'w', buffering = 0)
#  subprocess.call( [ context['isql_path'], dsn, '-q', '-i', f_apply_ddl_sql.name ], stdout = f_apply_ddl_log, stderr = subprocess.STDOUT)
#  flush_and_close( f_apply_ddl_log )
#  
#  #--------------------------------
#  
#  cur = db_conn.cursor()
#  try:
#      cur.execute( "insert into persons values (1, 'One', 'some_address', 'some_blob_info')" )
#      db_conn.commit()
#  except Exception as e:
#      print('Got exception:', sys.exc_info()[0])
#      print(e[0])
#  
#  finally:
#      db_conn.close()
#      cur.close()
#  
#  if fb_major >= 4.0:
#      runProgram( context['isql_path'], ['-q', dsn], 'ALTER EXTERNAL CONNECTIONS POOL CLEAR ALL;' )
#  
#  cleanup( (f_apply_ddl_sql.name, f_apply_ddl_log.name, fdb_repl) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Got exception: <class 'fdb.fbcore.DatabaseError'>
    Error while executing SQL statement:
    - SQLCODE: -901
    - Execute statement error at isc_dsql_prepare :
    335544359 : attempted update of read-only column PERSONS.COMP
    Statement : insert into "PERSONS" ("ID", "NAME", "ADDRESS", "INFO", "COMP") values (?, ?, ?, ?, ?)
    Data source : Firebird::C:\\FBTESTING\\qabt-repo	mp	mp_5972_repl.fdb
    - At block line: 9, col: 5
    - At trigger 'PERSONS_REPLICATE'
  """

@pytest.mark.version('>=3.0.6')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


