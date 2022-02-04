#coding:utf-8

"""
ID:          gtcs.external-file-04-C
FBTEST:      functional.gtcs.external_file_04_d_int128
TITLE:       Test for external table with field of INT128 datatype
DESCRIPTION:
  There is no similar test in GTCS, but for INTEGER datatype see:
  https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/EXT_REL_0_4_D.script
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db', substitutions=[('[ \t]+', ' ')])

expected_stdout = """
    F01 -170141183460469231731687303715884105728
    F01 -1
    F01 0
    F01 1
    F01 170141183460469231731687303715884105727
    Records affected: 5
"""

@pytest.mark.skip('FIXME: Not IMPLEMENTED')
@pytest.mark.version('>=4.0')
def test_1(act: Action):
    pytest.fail("Not IMPLEMENTED")

# test_script_1
#---
#
#  import os
#  import sys
#  import subprocess
#  import time
#
#  tmp_file = os.path.join(context['temp_directory'],'tmp_ext_04_d_int128.tmp')
#  if os.path.isfile( tmp_file):
#       os.remove( tmp_file )
#
#  this_fdb = db_conn.database_name
#
#  sql_cmd='''
#      connect 'localhost:%(this_fdb)s' user '%(user_name)s' password '%(user_password)s';
#      create table ext_table external file '%(tmp_file)s' (f01 int128);
#      commit;
#      insert into ext_table (f01) values ( 170141183460469231731687303715884105727);
#      insert into ext_table (f01) values (-170141183460469231731687303715884105728);
#      insert into ext_table (f01) values (1);
#      insert into ext_table (f01) values (-1);
#      insert into ext_table (f01) values (0);
#      commit;
#      set list on;
#      set count on;
#      select * from ext_table order by f01;
#  ''' % dict(globals(), **locals())
#
#  runProgram('isql', [ '-q' ], sql_cmd)
#
#  f_sql_chk = open( os.path.join(context['temp_directory'],'tmp_ext_04_d_int128.sql'), 'w')
#  f_sql_chk.write(sql_cmd)
#  f_sql_chk.close()
#
#  time.sleep(1)
#
#  os.remove(f_sql_chk.name)
#  os.remove( tmp_file )
#
#---
