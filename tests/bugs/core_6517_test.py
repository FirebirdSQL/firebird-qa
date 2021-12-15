#coding:utf-8
#
# id:           bugs.core_6517
# title:        Regression: CREATE DATABASE fails with 'Token unknown' error when DB name is enclosed in double quotes and 'DEFAULT CHARACTER SET' is specified after DB name
# decription:
#                   Confirmed bug on 4.0.0.2394, 3.0.8.33426
#                   Checked on 4.0.0.2401, 3.0.8.33435 -- all OK.
#
# tracker_id:   CORE-6517
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         None

import pytest
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file

# version: 3.0.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import time
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  temp_fdb = os.path.join( '$(DATABASE_LOCATION)', 'tmp_core_6517.tmp' )
#  db_conn.close()
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
#  cleanup( (temp_fdb,) )
#  con = fdb.create_database('create database "%s" default character set utf8' % temp_fdb)
#  # print( con.database_name )
#  con.close()
#
#  # CLEANUP
#  #########
#  time.sleep(1)
#  cleanup( (temp_fdb,) )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

test_db = temp_file('tmp_core_6517.fdb')

@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action, test_db: Path):
    act_1.isql(switches=[], input=f'create database "{act_1.get_dsn(test_db)}" default character set utf8;',
               connect_db=False)

