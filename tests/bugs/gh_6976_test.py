#coding:utf-8
#
# id:           bugs.gh_6976
# title:        Lack of proper clean up after failure to initialize shared memory
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6976
#               
#                   Test reads content of empty database (which is created auto) and makes several checks
#                   by writing this content to another .fdb file but WITHOUT last <N> pages.
#                   We have to start cut off last N pages and verisy that every time engine will instantly
#                   detect damage of database (i.e. not waiting for ~110 seconds as it was before fix).
#                   It is useless to cut off *last* 2..3 pages because engine makes reserving of space.
#                   Test settings for 'starting' page to be cuted off and number of pages are:
#                       SKIP_BACK_FROM_LAST_PAGE;
#                       NUM_OF_CUTED_LAST_PAGES
#                   Average time to wait exception with expected gdscode = 335544344 must be low: about 300...500 ms.
#                   Test used THRESHOLD_FOR_MAKE_CONNECT_MS to alert if alert time is more than this time.
#               
#                   Confirmed on WI-V4.0.1.2606: needed to wait for exactly 110s after each page starting from N-3.
#                   Checked on 3.0.8.33501, 4.0.1.2613.
#                
# tracker_id:   
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  import codecs
#  import re
#  import time
#  from datetime import datetime as dt
#  from datetime import timedelta
#  
#  SKIP_BACK_FROM_LAST_PAGE = 3
#  NUM_OF_CUTED_LAST_PAGES = 20
#  THRESHOLD_FOR_MAKE_CONNECT_MS = 1000
#  
#  db_source = db_conn.database_name
#  
#  cur = db_conn.cursor()
#  cur.execute('select m.mon$page_size,m.mon$pages from mon$database m')
#  for r in cur:
#      db_page_size = r[0]
#      db_pages_cnt = r[1]
#  
#  cur.close()
#  db_conn.close()
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
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
#  def try_cuted_off_db(dbsrc, dbtgt, db_page_size, db_pages_cnt, cut_off_pages_cnt):
#      
#      global dt, cleanup 
#  
#      cleanup( (dbtgt,) )
#  
#      with open(dbsrc, 'rb') as f:
#          fdb_binary_content = f.read( db_page_size * (db_pages_cnt - cut_off_pages_cnt) )
#  
#      w = open(dbtgt, 'wb')
#      w.write(fdb_binary_content)
#      w.close()
#  
#      msg_suffix = 'on attempt to connect to DB with missed last %d pages' % cut_off_pages_cnt
#  
#      da = dt.now()
#      diff_ms = -1
#      try:
#          dsn_cutoff = 'localhost:' + dbtgt
#          #########################
#          ###   c o n n e c t   ###
#          #########################
#          con = fdb.connect(dsn = dsn_cutoff)
#          # print('UNEXPECTED SUCCESS ' + msg_suffix )
#          con.close()
#      except Exception,e:
#          db = dt.now()
#          diff_ms = (db-da).seconds*1000 + (db-da).microseconds//1000
#          gds = e[2]
#          if gds <> 335544344:
#              print( 'Expected fail ' + msg_suffix + ' with unexpected gdscode: ' + str(e[2]) )
#  
#      cleanup( (dbtgt,) )
#  
#      return diff_ms
#  
#  #-----------------------
#  
#  def median(lst):
#      n = len(lst)
#      s = sorted(lst)
#      return (sum(s[n//2-1:n//2+1])/2.0, s[n//2])[n % 2] if n else None
#  
#  #-----------------------
#  
#  db_target = os.path.join(context['temp_directory'],'tmp_6976.cuted_off.fdb')
#  
#  ##################
#  ###   L O O P  ###
#  ##################
#  connect_establishing_ms = []
#  for i in range(SKIP_BACK_FROM_LAST_PAGE, SKIP_BACK_FROM_LAST_PAGE + NUM_OF_CUTED_LAST_PAGES, 1):
#      ms = try_cuted_off_db( db_source, db_target, db_page_size, db_pages_cnt, i)
#      if ms >= 0:
#          connect_establishing_ms.append( ms )
#  
#  failed_connections_count = len(connect_establishing_ms)
#  
#  if failed_connections_count > 0:
#      avg_ms = sum(connect_establishing_ms) / failed_connections_count
#  
#      print( 'Average time acceptable.' if avg_ms < THRESHOLD_FOR_MAKE_CONNECT_MS 
#             else 'Average time to get error because of broken DB is too long: %d ms, evaluated after get %d results. Threshold is %d ms.'
#                  % (avg_ms, failed_connections_count, THRESHOLD_FOR_MAKE_CONNECT_MS )
#           )
#  else:
#      print('UNEXPECTED FINAL: ENGINE COULD NOT DETECT DAMAGE OF DATABASE.')
#  
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    Average time acceptable.
"""

@pytest.mark.version('>=3.0.8')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_1(act_1: Action):
    pytest.fail("Test not IMPLEMENTED")
