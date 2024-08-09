#coding:utf-8

"""
ID:          issue-6391
ISSUE:       6391
TITLE:       Error "connection lost to database" could happen when application creates few local attachments (using XNET) simultaneously
DESCRIPTION:
    Test uses 15 threads and each of them launches loop for 10 iterations with making attach/detach from DB.
    Each instance of worker thread has dict() for storing its ID (as a key) and pair of values (success and fail count) as value.

    We have to ensure at the final point that for every of <THREADS_CNT> threads:
    * 1) number of SUCCESSFUL attempts is equal to limit that is declared here as LOOP_CNT.
    * 2) number of FAILED attempts is ZERO.

    Confirmed bug on 4.0.0.1598, 3.0.5.33166 (checked both SS and CS).
    It was enough 3 threads (which tried to establish attachments at the same time) to get runtime error:
    "- SQLCODE: -901 / - connection lost to database".

    Checked on 4.0.0.1607, 3.0.5.33171.
JIRA:        CORE-6142
FBTEST:      bugs.core_6142
NOTES:
    [20.08.2022] pzotov
    Confirmed again problem with 4.0.0.1598, 3.0.5.33166.
    Checked on 5.0.0.591, 4.0.1.2692, 3.0.8.33535
"""

import os
import threading
import datetime as py_dt
import time

import pytest
from firebird.qa import *
from firebird.driver import connect, driver_config, NetProtocol

###########################
###    S E T T I N G S  ###
###########################

# Number of threads to start:
THREADS_CNT = 15

# Number of iterations to make connect /  disconnect for every started thread:
LOOP_CNT = 10


tmp_user = user_factory('db', name='tmp$core_6142', password='123', plugin = 'Srp')
db = db_factory()

act = python_act('db', substitutions=[('[ \t]+', ' '), ('^((?!SQLCODE|SQLSTATE|[Cc]onnection|OVERALL RESULT).)*$', '')])

#---------------------
def showtime():
     return ''.join( (py_dt.datetime.now().strftime("%H:%M:%S.%f")[:11],'.') )

#---------------------

class workerThread(threading.Thread):
   def __init__(self, db_cfg_object, thr_idx, threads_cnt, num_of_iterations, usr):
      threading.Thread.__init__(self)
      self.db_cfg_object = db_cfg_object
      self.thr_idx = thr_idx
      self.threads_cnt = threads_cnt
      self.num_of_iterations = num_of_iterations
      self.usr = usr

      self.results_dict = { thr_idx : [0,0] }
      #fb_cset_lst = ['dos437', 'dos850', 'dos865', 'dos852', 'dos857', 'dos860','dos861', 'dos863', 'dos737', 'dos775', 'dos858', 'dos862', 'dos864', 'dos866', 'dos869', 'win1250', 'win1251', 'win1252', 'win1253', 'win1254', 'win1255', 'win1256',  'win1257', 'iso_8859_1', 'iso_8859_2', 'iso_8859_3', 'iso_8859_4', 'iso_8859_5', 'iso_8859_6', 'iso_8859_7', 'iso_8859_8', 'iso_8859_9']
      #self.db_cfg_object.charset.value = fb_cset_lst[thr_idx]
      
   def run(self):
      print( showtime(), f"Starting thread {self.thr_idx} / {self.threads_cnt}" )
      make_db_attach(self)
      print( showtime(), f"Exiting thread {self.thr_idx} / {self.threads_cnt}" )

   def show_results(self):
       for k,v in sorted( self.results_dict.items() ):
           print( "ID of thread: %3d. OVERALL RESULT: PASSED=%d, FAILED=%d" % ( k, v[0], v[1] ) )

#---------------------

def make_db_attach(thread_object):

   i = 0
   mon_sql = f"select count(*) from mon$attachments where mon$user = '{thread_object.usr.name.upper()}'"

   while i < thread_object.num_of_iterations:

      con = None
      att = 0

      msg_prefix = f"Thread {thread_object.thr_idx}, iter {i}/{thread_object.num_of_iterations-1}"
      print( showtime(), f"{msg_prefix} - trying to connect" )

      try:
          with connect( thread_object.db_cfg_object.name, user = thread_object.usr.name, password = thread_object.usr.password ) as con:
              print( showtime(), f"{msg_prefix}: created att = {con.info.id}" ) # , charset = {con.charset}" )

              # Accumulate counter of SUCCESSFULY established attachments:
              thread_object.results_dict[ thread_object.thr_idx ][0] += 1

      except Exception as e:
          # Accumulate counter of FAILED attachments:
          thread_object.results_dict[ thread_object.thr_idx ][1] += 1
          print(e)


      i += 1
#---------------------


@pytest.mark.version('>=3.0.5')
@pytest.mark.platform('Windows')
def test_1(act: Action, tmp_user: User, capsys):

    srv_config = driver_config.register_server(name = 'test_srv_core_6142', config = '')

    # Create new threads:
    # ###################
    threads_list=[]
    for thr_idx in range(0, THREADS_CNT):
        
        db_cfg_object = driver_config.register_database(name = f'test_db_core_6142_{thr_idx}')
        db_cfg_object.database.value = str(act.db.db_path)
        db_cfg_object.server.value = 'test_srv_core_6142'
        db_cfg_object.protocol.value = NetProtocol.XNET

        threads_list.append( workerThread( db_cfg_object, thr_idx, THREADS_CNT, LOOP_CNT, tmp_user ) )

    # Start new Threads
    # #################
    for t in threads_list:
        t.start()

    # Wait for all threads to complete
    for t in threads_list:
        t.join()

    act.expected_stdout = ''
    for t in threads_list:
        t.show_results()
        act.expected_stdout += 'ID of thread: %d. OVERALL RESULT: PASSED=%d, FAILED=%d\n' % (t.thr_idx, LOOP_CNT, 0)

    #print( showtime(), "##### Exiting Main Thread #####\\n")
   
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
