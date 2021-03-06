#coding:utf-8
#
# id:           bugs.core_6142
# title:        Error "connection lost to database" could happen when application creates few local attachments (using XNET) simultaneously
# decription:   
#                   Test uses 15 threads and each of them launches loop for 10 iterations with making attach/detach from DB.
#                   We use Python package with name "threading" here, but it should be declared as global inside class because of fbtest specific
#                   (otherwise test will failed with message "global name 'threading' is not defined").
#                   No such declaration is needed in normal way (i.e. when running code directly from Python, w/o using fbtest).
#                   Each instance of worker thread has dict() for storing its ID (as a key) and pair of values (success and fail count) as value.
#               
#                   We have to ensure at the final point that for every of <THREADS_CNT> threads:
#                   * 1) number of SUCCESSFUL attempts is equal to limit that is declared here as LOOP_CNT. 
#                   * 2) number of FAILED attempts is ZERO.
#               
#                   Confirmed bug on 4.0.0.1598, 3.0.5.33166 (checked both SS and CS). 
#                   It was enough 3 threads (which tried to establish attachments at the same time) to get runtime error:
#                   "- SQLCODE: -901 / - connection lost to database".
#               
#                   Checked on 4.0.0.1607, 3.0.5.33171. 
#                   :: NB :: 
#                   Execution time for this test strongly depends on major version and server mode:
#                       4.0 Classic: ~9"; 3.0.5 Classic: ~5";
#                       4.0 Super:   ~5"; 3.0.5 Super:   ~1".
#                
# tracker_id:   CORE-6142
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.5
# resources: None

substitutions_1 = [('^((?!OVERALL RESULT).)*$', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import threading
#  import datetime as py_dt
#  import time
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  
#  DB_PROT = 'xnet://'
#  DB_NAME = os.path.join(context['temp_directory'],'bugs.core_6142.fdb')
#  DB_USER = user_name
#  DB_PSWD = user_password
#  
#  LOOP_CNT=10
#  THREADS_CNT=15
#  
#  def showtime():
#       global py_dt
#       return ''.join( (py_dt.datetime.now().strftime("%H:%M:%S.%f")[:11],'.') )
#  
#  class workerThread(threading.Thread):
#     global threading, showtime, make_db_attach
#     def __init__(self, threadID, name, num_of_iterations):
#        threading.Thread.__init__(self)
#        self.threadID = threadID
#        self.name = name
#        self.num_of_iterations = num_of_iterations
#        self.results_dict = { threadID : [0,0] }
#     def run(self):
#        print( showtime(), "Starting " + self.name )
#        
#        make_db_attach( self.threadID, self.name, self.num_of_iterations, self.results_dict )
#  
#        print( showtime(), "Exiting " + self.name)
#     
#     def show_results(self):
#         for k,v in sorted( self.results_dict.items() ):
#             print( "ID of thread: %3d. OVERALL RESULT: PASSED=%d, FAILED=%d" % ( k, v[0], v[1] ) )
#  
#  def make_db_attach( threadID, threadName, num_of_iterations, results_dict ):
#     global DB_PROT, DB_NAME, DB_USER, DB_PSWD, FB_CLNT
#     global showtime
#     i = 1
#     while i<= num_of_iterations:
#  
#        con = None
#        att = 0
#        #print( showtime(), "%(threadName)s, iter %(i)s" % locals(), " - trying to: fdb.connect( dsn = '%(DB_PROT)s%(DB_NAME)s', user = '%(DB_USER)s', password = %(DB_PSWD)s, fb_library_name = '%(FB_CLNT)s' ) \\n" % globals() )
#        print( showtime(), "%(threadName)s, iter %(i)s" % locals(), " - trying to: fdb.connect( dsn = '%(DB_PROT)s%(DB_NAME)s' )\\n" % globals() )
#  
#        try:
#            #con = fdb.connect( dsn = DB_PROT + DB_NAME, user = DB_USER, password = DB_PSWD, fb_library_name = FB_CLNT )
#            con = fdb.connect( dsn = DB_PROT + DB_NAME, user = DB_USER, password = DB_PSWD )
#            att = con.attachment_id
#            fbv = con.firebird_version
#            print( showtime(), "%(threadName)s, iter %(i)s: attach_id=%(att)s has been created FB version: %(fbv)s.\\n" % locals() )
#  
#            if False:
#                cur = con.cursor()
#                cur.execute('select count(*) from ( select 1 x from rdb$types a,rdb$types b,(select 1 i from rdb$types rows ( 30+rand()*30 ) ) )' )
#                for r in cur:
#                    pass
#                cur.close()
#  
#            print( showtime(), "%(threadName)s, iter %(i)s: attach_id=%(att)s is to be closed.\\n" % locals() )
#            con.close()
#            print( showtime(), "%(threadName)s, iter %(i)s: attach_id=%(att)s has been closed.\\n" % locals() )
#            results_dict[ threadID ][0] += 1
#  
#        except Exception,e:
#            results_dict[ threadID ][1] += 1
#            for k,x in enumerate(e):
#                print( showtime(), "%(threadName)s, iter %(i)s: exception occured:\\n%(x)s\\n" % locals() )
#  
#        i += 1
#  
#  
#  # Create new threads:
#  # ###################
#  threads_list=[]
#  for i in range(0, THREADS_CNT):
#      threads_list.append( workerThread( i+1, "Thread-%d" % (i+1), LOOP_CNT) )
#  
#  # Start new Threads
#  # #################
#  for t in threads_list:
#      t.start()
#  
#  
#  # Wait for all threads to complete
#  for t in threads_list:
#      t.join()
#  
#  for t in threads_list:
#      t.show_results()
#  
#  print( showtime(), "##### Exiting Main Thread #####\\n")
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID of thread:   1. OVERALL RESULT: PASSED=10, FAILED=0
    ID of thread:   2. OVERALL RESULT: PASSED=10, FAILED=0
    ID of thread:   3. OVERALL RESULT: PASSED=10, FAILED=0
    ID of thread:   4. OVERALL RESULT: PASSED=10, FAILED=0
    ID of thread:   5. OVERALL RESULT: PASSED=10, FAILED=0
    ID of thread:   6. OVERALL RESULT: PASSED=10, FAILED=0
    ID of thread:   7. OVERALL RESULT: PASSED=10, FAILED=0
    ID of thread:   8. OVERALL RESULT: PASSED=10, FAILED=0
    ID of thread:   9. OVERALL RESULT: PASSED=10, FAILED=0
    ID of thread:  10. OVERALL RESULT: PASSED=10, FAILED=0
    ID of thread:  11. OVERALL RESULT: PASSED=10, FAILED=0
    ID of thread:  12. OVERALL RESULT: PASSED=10, FAILED=0
    ID of thread:  13. OVERALL RESULT: PASSED=10, FAILED=0
    ID of thread:  14. OVERALL RESULT: PASSED=10, FAILED=0
    ID of thread:  15. OVERALL RESULT: PASSED=10, FAILED=0
  """

@pytest.mark.version('>=3.0.5')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


