#coding:utf-8
#
# id:           bugs.core_5645
# title:        Wrong transaction can be passed to external engine
# decription:   
#                   Implemented according to notes given by Adriano in the ticket 27-oct-2017 02:41.
#                   Checked on:
#                       4.0.0.1743 SS: 2.719s.
#                       4.0.0.1740 SC: 2.531s.
#                       4.0.0.1714 CS: 11.750s.
#                       3.0.6.33236 SS: 1.141s.
#                       3.0.6.33236 CS: 2.563s.
#                       3.0.5.33221 SC: 3.812s.
# tracker_id:   CORE-5645
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = [('INFO_BLOB_ID.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import subprocess
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
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
#          info blob sub_type text
#      );
#  '''
#  
#  
#  fdb_repl = os.path.join(context['temp_directory'],'tmp_5645_repl.fdb')
#  cleanup( (fdb_repl,) )
#  
#  con_repl = fdb.create_database(  dsn = 'localhost:%(fdb_repl)s' % locals() )
#  con_repl.execute_immediate( table_ddl )
#  con_repl.commit()
#  con_repl.close()
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
#  f_apply_ddl_sql = open( os.path.join(context['temp_directory'],'tmp_5645.sql'), 'w', buffering = 0)
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
#  cur.execute( "insert into persons values (1, 'One', 'some_address', 'some_blob_info')" )
#  db_conn.commit()
#  db_conn.close()
#  
#  if fb_major >= 4.0:
#      runProgram( 'isql', ['-q', dsn], 'ALTER EXTERNAL CONNECTIONS POOL CLEAR ALL;' )
#  
#  runProgram( 'isql', ['-q', 'localhost:%(fdb_repl)s' % locals()], 'set list on; set count on; select id,name,address,info as info_blob_id from persons;rollback; drop database;' )
#  
#  cleanup( (f_apply_ddl_sql,f_apply_ddl_log) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    NAME                            One
    ADDRESS                         some_address
    INFO_BLOB_ID                    80:0
    some_blob_info

    ID                              1
    NAME                            One
    ADDRESS                         <null>
    INFO_BLOB_ID                    80:1
    some_blob_info
    Records affected: 2
  """

@pytest.mark.version('>=3.0.3')
@pytest.mark.xfail
def test_core_5645_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


