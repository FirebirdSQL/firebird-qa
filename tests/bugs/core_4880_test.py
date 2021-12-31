#coding:utf-8
#
# id:           bugs.core_4880
# title:        Increase speed of creating package when number of its functions more than several hundreds
# decription:
#                   Ticket URL: https://github.com/FirebirdSQL/firebird/issues/5175
#
#                   Test creates package with N_LIMIT functions and the same number of standalone PSQL functions.
#                   We measure separately N_MEASURES times duration of:
#                       1. PSQL object(s) compilation and
#                       2. COMMIT of their BLR
#                   Fix that was done for this ticket relates mostly to the RATIO between "1" and "2" and (secondary) to their
#                   absolute values:
#                   -------------------------------------------------------------------------------------------------------------------
#                   |                        |   Package with 5'000 functions     |            |   5'000 standalone functions         |
#                   |                        |------------------------------------|            |--------------------------------------|
#                   |                        |compile    commit     time ratio:   |            |compile    commit      time ratio:    |
#                   |Build                   |time, ms   time, ms   commit/compile|            |time, ms   time, ms    commit/compile |
#                   |------------------------|------------------------------------|------------|--------------------------------------|
#                   |3.0.0.31374 Beta 1      |    8662     108479       12.52     |            |    6066     114489         18.87     |
#                   |3.0.0.31896 Beta 2      |    8674     113157       13.05     |            |    5868     113167         19.29     |
#                   |3.0.0.32136 RC 1        |    9601       5348        0.56     |            |    5934       6724          1.06     |
#                   |3.0.8.33540             |   11308       5794        0.51     |            |    4445       5617          1.26     |
#                   |4.0.1.2672              |    9841       6130        0.62     |            |    4864       6413          1.32     |
#                   |5.0.0.321               |   10734       4346        0.40     |            |    4803       6497          1.35     |
#                   -------------------------------------------------------------------------------------------------------------------
#                                                                        ^^^^                                                ^^^^
#                   One may see that although compiling time increased for package and reduced for standalone functions (since RC-1),
#                   time ot COMMIT was reduced  significantly.
#
#                   Test was fully re-implemented in order to take in account exactly *this* change rather than wrong way (when we
#                   did analysis of ratio between *total* time of compilation + commit forpackage vs N_LIMIT standalone functions).
#
#                   Within each measure we create new database, make its FW equals to OFF and do following:
#                   * create poackage with N_LIMIT functions
#                   * commit
#                   * create N_LIMIT standalone functions
#                   * commit
#
#                   Values of CPU User Time before and after every action are taken. Difference between them can be consider as much more
#                   accurate time estimation. Then we calculate RATIO between these differences, and so we can evaluate how long COMMIT was
#                   in comparison to DML.
#                   We perform this N_MEASURES times and get list of ratios for both cases (i.e. one list for package with 5'000 functions
#                   and second for 5'000 standalone functions).
#                   Then we evaluate MEDIAN of ratios for each list.
#                   Finally, we compare these medians with THRESHOLDS, which values have been taken from the table that is shown above,
#                   with increasing by approx. 20%
#
#                   Checked on Windows:
#                       5.0.0.321 : 68.307s.
#                       4.0.1.2672 : 69.518s.
#                       3.0.8.33540 : 68.340s.
#                   Checked on Linux:
#                       5.0.0.325 : 49.79s.
#                       4.0.1.2672 : 49.663s
#                       3.0.8.33533 : 52.483s
#                   Switching from SS to CS has no effect: elapsed time remains almost the same.
#
# tracker_id:   CORE-4880
# min_versions: ['3.0.0']
# versions:     3.0
# qmid:

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import psutil
#  from fdb import services
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_conn.close()
#
#  #------------------
#  def median(lst):
#      n = len(lst)
#      s = sorted(lst)
#      return (sum(s[n//2-1:n//2+1])/2.0, s[n//2])[n % 2] if n else None
#  #------------------
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
#            print('type(f_names_list[i])=',type(f_names_list[i]))
#            del_name = None
#
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#
#  #------------------
#
#  svc = services.connect(host='localhost', user='sysdba', password='masterkey')
#
#  ###########################
#  ###   S E T T I N G S   ###
#  ###########################
#  # How many times we call PSQL code (two stored procedures:
#  # one for performing comparisons based on LIKE, second based on SIMILAR TO statements):
#  N_MEASURES = 15
#
#  # How many functions must be created on each iteration:
#  N_LIMIT = 1100
#
#  ###############################
#  ###   T H R E S H O L D S   ###
#  ###############################
#  if os.name == 'nt':
#      MAX_TIME_RATIOS_COMMIT_TO_COMPILE = {'packaged' : 0.55, 'standalone' : 1.50}
#  else:
#      MAX_TIME_RATIOS_COMMIT_TO_COMPILE = {'packaged' : 0.55, 'standalone' : 0.50}
#
#
#  func_headers_ddl = ''.join( [ '\\n  function fn_%d returns int;' % i for i in range(N_LIMIT) ] )
#  func_bodies_ddl = ''.join( [ '\\n  function fn_%d returns int as begin return %d; end' % (i,i) for i in range(N_LIMIT) ] )
#
#  pkg_header_ddl = '\\n'.join( ('create or alter package huge as\\nbegin', func_headers_ddl, 'end') )
#  pkg_body_ddl = '\\n'.join( ('recreate package body huge as\\nbegin', func_bodies_ddl, 'end') )
#
#
#  temp_fdb = os.path.join( '$(DATABASE_LOCATION)', 'tmp_core_4880.tmp' )
#
#  sp_time = {}
#  for i in range(0, N_MEASURES):
#      for ftype in ('packaged', 'standalone'):
#
#          cleanup( (temp_fdb,) )
#
#          con=fdb.create_database(dsn = 'localhost:%s' % temp_fdb)
#          con.close()
#          svc.set_write_mode( temp_fdb, services.WRITE_BUFFERED)
#          con=fdb.connect(dsn = 'localhost:%s' % temp_fdb)
#
#          cur=con.cursor()
#          cur.execute('select mon$server_pid as p from mon$attachments where mon$attachment_id = current_connection')
#          fb_pid = int(cur.fetchone()[0])
#          cur.close()
#
#
#          fb_info_a = psutil.Process(fb_pid).cpu_times()
#          if ftype == 'packaged':
#              con.execute_immediate(pkg_header_ddl)
#              con.execute_immediate(pkg_body_ddl)
#          else:
#              for k in range(0,N_LIMIT):
#                  con.execute_immediate( 'create or alter function sf_%d returns int as begin return %d; end' % (k,k)  )
#
#          fb_info_b = psutil.Process(fb_pid).cpu_times()
#          con.commit()
#          fb_info_c = psutil.Process(fb_pid).cpu_times()
#
#          cpu_time_for_compile = max(fb_info_b.user - fb_info_a.user, 0.000001)
#          cpu_time_for_commit = fb_info_c.user - fb_info_b.user
#
#          sp_time[ ftype, i ]  = cpu_time_for_commit / cpu_time_for_compile
#
#          con.drop_database()
#          cleanup( (temp_fdb,) )
#
#  svc.close()
#
#  commit_2_compile_ratio_for_package = [round(v,2) for k,v in sp_time.items() if k[0] == 'packaged']
#  commit_2_compile_ratio_for_standal = [round(v,2) for k,v in sp_time.items() if k[0] == 'standalone']
#
#  #print('RATIOS:')
#  #print('commit_2_compile_ratio_for_package=',commit_2_compile_ratio_for_package)
#  #print('commit_2_compile_ratio_for_standal=',commit_2_compile_ratio_for_standal)
#  #print('MEDIANS:')
#  #print('median(commit_2_compile_ratio_for_package)=',median(commit_2_compile_ratio_for_package))
#  #print('median(commit_2_compile_ratio_for_standal)=',median(commit_2_compile_ratio_for_standal))
#
#  actual_time_ratios_commit2compile = { 'packaged' : median(commit_2_compile_ratio_for_package), 'standalone': median(commit_2_compile_ratio_for_standal) }
#
#  msg_prefix = 'Time ratio between COMMIT and COMPILE '
#  for ftype in ('packaged', 'standalone'):
#      msg = msg_prefix + 'for ' + ftype + ' PSQL objects: '
#      if actual_time_ratios_commit2compile[ ftype ] < MAX_TIME_RATIOS_COMMIT_TO_COMPILE[ ftype ]:
#          print( msg + 'acceptable')
#      else:
#          print( msg + 'UNACCEPTABLE: greater than threshold = ', MAX_TIME_RATIOS_COMMIT_TO_COMPILE[ ftype ])
#          print( 'Check result of %d measures:' % N_MEASURES )
#          lst = commit_2_compile_ratio_for_package if ftype == 'packaged' else commit_2_compile_ratio_for_standal
#          for i,p in enumerate(lst):
#              print('%3d' %i, ':', '%12.2f' % p)
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    Time ratio between COMMIT and COMPILE for packaged PSQL objects: acceptable
    Time ratio between COMMIT and COMPILE for standalone PSQL objects: acceptable
"""

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(act_1: Action):
    pytest.fail("Test not IMPLEMENTED")

# Reimplementation from previous version
# ======================================
#from zipfile import Path

## version: 3.0
## resources: None

#substitutions_1 = []

#init_script_1 = """
    #recreate table log(
         #standalone_func_beg timestamp default null,
         #standalone_func_end timestamp default null,
         #pkg_head_n_body_beg timestamp default null,
         #pkg_head_n_body_end timestamp default null
    #);
    #commit;
    #insert into log default values;
    #commit;
#"""

#db_1 = db_factory(sql_dialect=3, init=init_script_1)

## test_script_1
##---
## import os
##  import zipfile
##
##  os.environ["ISC_USER"] = user_name
##  os.environ["ISC_PASSWORD"] = user_password
##
##  db_conn.close()
##  runProgram('gfix',['-w','async',dsn])
##
##  zf = zipfile.ZipFile( os.path.join(context['files_location'],'core_4880.zip') )
##  zf.extractall( context['temp_directory'] )
##  zf.close()
##  runProgram('isql',[dsn,'-q','-i', os.path.join(context['temp_directory'],'core_4880_fnc.tmp') ])
##  runProgram('isql',[dsn,'-q','-i', os.path.join(context['temp_directory'],'core_4880_pkg.tmp') ])
##
##  os.remove( os.path.join(context['temp_directory'],'core_4880_fnc.tmp') )
##  os.remove( os.path.join(context['temp_directory'],'core_4880_pkg.tmp') )
##
##  script="""set list on;
##  set term ^;
##  execute block as
##  begin
##    rdb$set_context('USER_SESSION', 'MAX_ACCEPTABLE_RATIO', '2');
##    --                                                       ^
##    --                                               #################
##    --                                               T H R E S H O L D
##    --                                               #################
##  end
##  ^
##  set term ;^
##
##  select iif( x.ratio < cast( rdb$get_context('USER_SESSION', 'MAX_ACCEPTABLE_RATIO') as int ),
##              'Ratio is acceptable',
##              'Regression, ratio >= ' || rdb$get_context('USER_SESSION', 'MAX_ACCEPTABLE_RATIO') || 'x'
##            ) as result_msg
##        --, x.*
##    from (
##    select
##      standalone_func_sec
##      ,pkg_head_n_body_sec
##      ,cast( iif( pkg_head_n_body_sec > standalone_func_sec, 1.00 * pkg_head_n_body_sec / standalone_func_sec, 1.00 * standalone_func_sec / pkg_head_n_body_sec ) as numeric(12,2) ) as ratio
##      ,cast( 1.00 * pkg_head_n_body_sec / standalone_func_sec as numeric(12,2) ) package_vs_standalone
##      ,cast( 1.00 * standalone_func_sec / pkg_head_n_body_sec as numeric(12,2) ) standalone_vs_package
##    from (
##      select
##         nullif( datediff(second from standalone_func_beg to standalone_func_end), 0) standalone_func_sec
##        ,nullif( datediff(second from pkg_head_n_body_beg to pkg_head_n_body_end), 0) pkg_head_n_body_sec
##      from log
##    )
##  ) x;
##  """
##  runProgram('isql',[dsn,'-q'],script)
##---

#act_1 = python_act('db_1', substitutions=substitutions_1)

#expected_stdout_1 = """
    #RESULT_MSG                      Ratio is acceptable
#"""

#@pytest.mark.version('>=3.0')
#def test_1(act_1: Action):
    ## Read FNC scripts from zip file and execute it
    #script_file = Path(act_1.files_dir / 'core_4880.zip',
                    #at='core_4880_fnc.tmp')
    #act_1.script = script_file.read_text()
    #act_1.execute()
    ## Read PKG scripts from zip file and execute it
    #script_file = Path(act_1.files_dir / 'core_4880.zip',
                    #at='core_4880_pkg.tmp')
    #act_1.script = script_file.read_text()
    #act_1.execute()
    ## Check
    #test_script = """
    #set list on;
    #set term ^;
    #execute block as
    #begin
      #rdb$set_context('USER_SESSION', 'MAX_ACCEPTABLE_RATIO', '2');
      #--                                                       ^
      #--                                               #################
      #--                                               T H R E S H O L D
      #--                                               #################
    #end
    #^
    #set term ;^

    #select iif(x.ratio < cast( rdb$get_context('USER_SESSION', 'MAX_ACCEPTABLE_RATIO') as int ),
               #'Ratio is acceptable',
               #'Regression, ratio >= ' || rdb$get_context('USER_SESSION', 'MAX_ACCEPTABLE_RATIO') || 'x'
              #) as result_msg
          #--, x.*
      #from (
      #select
        #standalone_func_sec,
        #pkg_head_n_body_sec,
        #cast(iif( pkg_head_n_body_sec > standalone_func_sec, 1.00 * pkg_head_n_body_sec / standalone_func_sec, 1.00 * standalone_func_sec / pkg_head_n_body_sec ) as numeric(12,2) ) as ratio,
        #cast(1.00 * pkg_head_n_body_sec / standalone_func_sec as numeric(12,2)) package_vs_standalone,
        #cast(1.00 * standalone_func_sec / pkg_head_n_body_sec as numeric(12,2)) standalone_vs_package
      #from (
        #select
           #nullif(datediff(second from standalone_func_beg to standalone_func_end), 0) standalone_func_sec,
           #nullif(datediff(second from pkg_head_n_body_beg to pkg_head_n_body_end), 0) pkg_head_n_body_sec
        #from log
      #)
    #) x;
#"""
    #act_1.reset()
    #act_1.expected_stdout = expected_stdout_1
    #act_1.isql(switches=['-q'], input=test_script)
    #assert act_1.clean_stdout == act_1.clean_expected_stdout
