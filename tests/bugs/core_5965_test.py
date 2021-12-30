#coding:utf-8
#
# id:           bugs.core_5965
# title:        FB3 Optimiser chooses less efficient plan than FB2.5 optimiser
# decription:
#                   Filling of database with data from ticket can take noticable time.
#                   Instead of this it was decided to extract form ZIP archieve .fbk and then to restore it.
#                   Instead of actual execution we can only obtain PLAN by querying cursor read-only property "plan"
#                   than becomes not null after obtaining at least one record for executing statement.
#                   We can get only one row without need to show its data by trivial cursor handling like this:
#                   ===
#                       cur.execute(sql)
#                       for r in cur:
#                           pass
#                           break
#                   ===
#                   Confirmed wrong plan for second expr in  4.0.0.1249, 3.0.4.33053
#                   Works fine in 4.0.0.1340, 3.0.5.33084
#
# tracker_id:   CORE-5965
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
import zipfile
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file, Database

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)
db_1_tmp = db_factory(sql_dialect=3, filename='tmp_core_5965.fdb', do_not_create=True)


# test_script_1
#---
#
#  import os
#  import fdb
#  import time
#  import zipfile
#  import difflib
#  import subprocess
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
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
#            del_name = None
#
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#
#  #--------------------------------------------
#
#
#
#  zf = zipfile.ZipFile( os.path.join(context['files_location'],'core_5965.zip') )
#  tmpfbk = 'core_5965.fbk'
#  zf.extract( tmpfbk, '$(DATABASE_LOCATION)')
#  zf.close()
#
#  tmpfbk='$(DATABASE_LOCATION)'+tmpfbk
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_core_5965.fdb'
#
#  f_restore_log=open( os.path.join(context['temp_directory'],'tmp_core_5965_restore.log'), 'w')
#  subprocess.check_call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                         "action_restore",
#                         "bkp_file", tmpfbk,
#                         "dbname", tmpfdb,
#                         "res_replace",
#                         "verbose"
#                        ],
#                        stdout=f_restore_log,
#                        stderr=subprocess.STDOUT)
#  flush_and_close( f_restore_log )
#
#  con=fdb.connect(dsn = 'localhost:'+tmpfdb)
#
#  # https://pythonhosted.org/fdb/reference.html#fdb.Cursor
#
#  cur_1=con.cursor()
#  cur_2=con.cursor()
#
#  sql_1='''
#      select 1
#      from opt_test
#      where
#          --sysid = 1 and
#          clid = 23 and
#          cust_type = 1 and
#          cust_id = 73
#          order by order_no desc
#      ;
#  '''
#
#  sql_2='''
#      select 2
#      from opt_test
#      where
#          sysid = 1 and
#          clid = 23 and
#          cust_type = 1 and
#          cust_id = 73
#          order by order_no desc
#      ;
#
#  '''
#
#  cur_1.execute(sql_1)
#  for r in cur_1:
#      pass
#      break
#
#  cur_2.execute(sql_2)
#  for r in cur_2:
#      pass
#      break
#
#  print( cur_1.plan )
#  print( cur_2.plan )
#
#  cur_1.close()
#  cur_2.close()
#  con.close()
#
#  # Cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (tmpfbk, tmpfdb, f_restore_log) )
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN SORT (OPT_TEST INDEX (O_CLID_CUSTTY_CUSTID))
    PLAN SORT (OPT_TEST INDEX (O_CLID_CUSTTY_CUSTID))
"""

fbk_file = temp_file('core_5965.fbk')

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, fbk_file: Path, db_1_tmp: Database, capsys):
    zipped_fbk_file = zipfile.Path(act_1.files_dir / 'core_5965.zip',
                                   at='core_5965.fbk')
    fbk_file.write_bytes(zipped_fbk_file.read_bytes())
    #
    with act_1.connect_server() as srv:
        srv.database.restore(backup=fbk_file, database=db_1_tmp.db_path)
        srv.wait()
    # Test
    with db_1_tmp.connect() as con:
        c1 = con.cursor()
        c2 = con.cursor()
        c1.execute("select 1 from opt_test where clid = 23 and cust_type = 1 and cust_id = 73 order by order_no desc")
        c1.fetchall()
        print(c1.statement.plan)
        #
        c2.execute("select 2 from opt_test where sysid = 1 and clid = 23 and cust_type = 1 and cust_id = 73 order by order_no desc")
        c2.fetchall()
        print(c2.statement.plan)
    # Check
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
