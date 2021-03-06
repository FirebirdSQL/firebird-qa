#coding:utf-8
#
# id:           bugs.core_5659
# title:        Bad PLAN generated for query on Firebird v3.0
# decription:   
#                    Test is based on data from original database that was provided in the ticket by its author.
#                    Lot of data from tables were removed in order to reduce DB size.
#                    Reproduced bug on 3.0.2.32708, 4.0.0.800
#                    Wrong plan was: 
#                        PLAN JOIN (A NATURAL, C INDEX (PK_EST_PRODUTO), B INDEX (PK_COM_PEDIDO))
#                    Elapsed time was more than 1.2 second.
#               
#                    All fine on:
#                        3.0.3.32838: OK, 5.922s.
#                        4.0.0.801: OK, 6.547s.
#                 
# tracker_id:   CORE-5659
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import time
#  import zipfile
#  import subprocess
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  
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
#  zf = zipfile.ZipFile( os.path.join(context['files_location'],'core_5659.zip') )
#  tmpfbk = 'core_5659.fbk'
#  zf.extract( tmpfbk, '$(DATABASE_LOCATION)')
#  zf.close()
#  
#  tmpfbk='$(DATABASE_LOCATION)'+tmpfbk
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_bad_plan_5659.fdb'
#  
#  f_restore_log=open( os.path.join(context['temp_directory'],'tmp_bad_plan_5659.log'), 'w')
#  subprocess.check_call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                         "action_restore",
#                         "bkp_file", tmpfbk,
#                         "dbname", tmpfdb,
#                         "res_replace"
#                        ],
#                        stdout=f_restore_log, 
#                        stderr=subprocess.STDOUT)
#  flush_and_close( f_restore_log )
#  
#  # should be empty:
#  ##################
#  with open( f_restore_log.name,'r') as f:
#    for line in f:
#        if line.split():
#          print('UNEXPECTED STDERR in '+f_restore_log.name+': '+line)
#  
#  
#  sqltxt='''
#      set planonly;
#      select
#          a.id_pedido_item,
#          c.descricao
#      from com_pedido b
#      join com_pedido_item a on a.id_pedido = b.id_pedido
#                      and ( not(a.id_produto =1 and a.id_pedido_item_pai is not null))
#      join est_produto c on c.id_produto = a.id_produto
#      where
#          -- b.dth_pedido between cast('10.12.16 05:00:00' as timestamp) and cast('10.12.16 20:00:00' as timestamp)
#          b.dth_pedido between ? and ?
#      ;
#  '''
#  
#  runProgram('isql', [ 'localhost:'+tmpfdb,'-q' ], sqltxt)
#  
#  
#  # Cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (f_restore_log, tmpfdb, tmpfbk) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN JOIN (B INDEX (COM_PEDIDO_IDX1), A INDEX (FK_COM_PEDIDO_ITEM_PEDIDO), C INDEX (PK_EST_PRODUTO))
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


