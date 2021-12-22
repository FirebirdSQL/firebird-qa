#coding:utf-8
#
# id:           functional.gtcs.external_file_09_d
# title:        GTCS/tests/external-file-09-d. Test for external table with field of DATE datatype
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/EXT_REL_0_9_D.script
#                   Checked on: 4.0.0.2240 SS: 2.473s; 3.0.7.33380 SS: 1.924s.
#                
# tracker_id:   
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import subprocess
#  import time
#  
#  tmp_file = os.path.join(context['temp_directory'],'tmp_ext_09_d.tmp')
#  if os.path.isfile( tmp_file):
#       os.remove( tmp_file )
#  
#  this_fdb = db_conn.database_name
#  
#  sql_cmd='''
#      connect 'localhost:%(this_fdb)s' user '%(user_name)s' password '%(user_password)s';
#      create table ext_table external file '%(tmp_file)s' (f01 date);
#      commit;
#      -- connect 'localhost:%(this_fdb)s' user '%(user_name)s' password '%(user_password)s';
#      insert into ext_table (f01) values ('28-June-94');
#      insert into ext_table (f01) values ('29-feb-4');
#      insert into ext_table (f01) values ('1-september-1');
#      insert into ext_table (f01) values ('1-january-0001');
#      insert into ext_table (f01) values ('31-december-9999');
#      insert into ext_table (f01) values (current_date);
#      insert into ext_table (f01) values (current_timestamp);
#      insert into ext_table (f01) values ('29-feb-9999');
#      commit;
#      set list on;
#      set count on;
#      select * from ext_table where f01<>current_date;
#      set count off;
#      select count(*) as this_day_count from ext_table where f01=current_date;
#      commit;
#  ''' % dict(globals(), **locals())
#  
#  runProgram('isql', [ '-q' ], sql_cmd)
#  
#  f_sql_chk = open( os.path.join(context['temp_directory'],'tmp_ext_09_d.sql'), 'w')
#  f_sql_chk.write(sql_cmd)
#  f_sql_chk.close()
#  
#  time.sleep(1)
#  
#  os.remove(f_sql_chk.name)
#  os.remove( tmp_file )
#  
#---
act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22018
    conversion error from string "29-feb-9999"
"""

expected_stdout_1 = """
    F01 1994-06-28
    F01 2004-02-29
    F01 2001-09-01
    F01 0001-01-01
    F01 9999-12-31
    Records affected: 5

    THIS_DAY_COUNT 2
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    pytest.fail("Test not IMPLEMENTED")


