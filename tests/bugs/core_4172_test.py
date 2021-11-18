#coding:utf-8
#
# id:           bugs.core_4172
# title:        Creating external function (udf) to not existing dll - and then procedure with it - crash server
# decription:
#
#                   *** FOR FB 4.X AND ABOVE  ***
#                       Added separate code for running on FB 4.0.x: we use create UDR function statement and specify
#                       non-existent library 'unknown_udf!UC_div'. The statement per se will pass and rdb$functions
#                       *will* contain record for just created function. But following COMMT will raise exception:
#                           Statement failed, SQLSTATE = HY000
#                           UDR module not loaded
#                           <localized message here>
#                       Then we rollback and query rdb$functions again. No record about this function must be there.
#
#                       STDERR is ignored in this test because of localized message about missed library.
#                       Checked on:
#                           4.0.0.1172: OK, 7.344s.
#                           4.0.0.1340: OK, 2.797s.
#                           4.0.0.1378: OK, 3.062s.
#
# tracker_id:   CORE-4172
# min_versions: ['3.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
import re
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file

# version: 3.0
# resources: None

substitutions_1 = [('.* at offset.*', '.* at offset')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.close()
#
#  #---------------------------------------------
#
#  def flush_and_close(file_handle):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f,
#      # first do f.flush(), and
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb'):
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#
#
#  #--------------------------------------------
#
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#              if os.path.isfile( f_names_list[i]):
#                  print('ERROR: can not remove file ' + f_names_list[i])
#
#  #--------------------------------------------
#
#  tmpfdb_1=os.path.join(context['temp_directory'],'tmp_4172_1.fdb')
#  tmpfdb_2=os.path.join(context['temp_directory'],'tmp_4172_2.fdb')
#
#  sql_chk='''
#      create database '%(tmpfdb_2)s';
#      commit;
#      create database '%(tmpfdb_1)s';
#
#      set autoddl off;
#      commit;
#
#      declare external function dummy_ext
#      integer
#      returns integer by value
#      entry_point 'dummy_ext'
#      module_name 'non_existing_udf.dll';
#      commit;
#
#      set term ^;
#      create procedure sp_test ( a_id integer ) returns  ( o_name integer ) as
#      begin
#        o_name = dummy_ext(a_id);
#        suspend;
#      end
#      ^
#      set term ;^
#      commit;
#
#      rollback;
#
#      connect '%(tmpfdb_2)s';
#      set list on;
#      select 1 as x from rdb$database;
#  ''' % locals()
#
#  f_list=[tmpfdb_1, tmpfdb_2]
#
#  # Cleanup BEFORE running script:
#  ################
#  cleanup( f_list )
#
#  runProgram( context['isql_path'],['-q'], sql_chk)
#
#  # Final cleanup:
#  ################
#  time.sleep(1)
#  cleanup( f_list )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    X                               1
"""

expected_stderr_1 = """
    Statement failed, SQLSTATE = 39000
    invalid request BLR at offset
    -function DUMMY_EXT is not defined
    -module name or entrypoint could not be found
"""

temp_db_1_a = temp_file('tmp_4172_1.fdb')
temp_db_1_b = temp_file('tmp_4172_2.fdb')

@pytest.mark.version('>=3.0,<4')
def test_1(act_1: Action, temp_db_1_a: Path, temp_db_1_b: Path):
    test_script = f"""
    create database '{str(temp_db_1_b)}';
    commit;
    create database '%(tmpfdb_1)s';

    set autoddl off;
    commit;

    declare external function dummy_ext
    integer
    returns integer by value
    entry_point 'dummy_ext'
    module_name 'non_existing_udf.dll';
    commit;

    set term ^;
    create procedure sp_test ( a_id integer ) returns  ( o_name integer ) as
    begin
      o_name = dummy_ext(a_id);
      suspend;
    end
    ^
    set term ;^
    commit;

    rollback;

    connect '{str(temp_db_1_b)}';
    set list on;
    select 1 as x from rdb$database;
    """
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.isql(switches=['-q'], input=test_script)
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout


# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

# test_script_2
#---
#
#  import os
#  import time
#  import subprocess
#  from fdb import services
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_conn.close()
#
#  #---------------------------------------------
#
#  def flush_and_close(file_handle):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f,
#      # first do f.flush(), and
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb'):
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#
#  #--------------------------------------------
#
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#              if os.path.isfile( f_names_list[i]):
#                  print('ERROR: can not remove file ' + f_names_list[i])
#
#  #--------------------------------------------
#
#
#  # STDERR: Statement failed, SQLSTATE = HY000
#  # STDERR: UDR module not loaded
#  #allowed_patterns = ( re.compile( '\\.*SQLSTATE\\s*=\\s*HY000', re.IGNORECASE),
#  #                     re.compile( '\\.*UDR\\s+module\\s+not\\s+(found|loaded)\\.*', re.IGNORECASE),
#  #                   )
#
#  sql_text='''
#      recreate view v_check as
#      select rdb$function_name, rdb$entrypoint, rdb$engine_name, rdb$legacy_flag
#      from rdb$functions
#      where rdb$system_flag is distinct from 1 and rdb$function_name starting with upper( 'the_' )
#      ;
#      commit;
#
#      set list on;
#      set term ^;
#      execute block returns( o_gdscode int ) as
#      begin
#          begin
#              execute statement
#                q'{
#                      create function the_div (
#                          n1 integer,
#                          n2 integer
#                      ) returns double precision
#                          external name 'unknown_udf!UC_div'
#                          engine udr
#                  }';
#                  -- was: external name 'udf_compat!UC_div'
#
#          when any do
#              begin
#                  o_gdscode = gdscode;
#              end
#          end
#          suspend;
#      end
#      ^
#      set term ;^
#
#      commit;
#
#      set blob all;
#      set count on;
#
#      select * from v_check;
#      rollback;
#
#      select * from v_check;
#      rollback;
#  '''
#
#  f_sql_chk = open( os.path.join(context['temp_directory'],'tmp_4172.sql') , 'w')
#  f_sql_chk.write(sql_text)
#  flush_and_close( f_sql_chk )
#
#  f_sql_log=open( os.path.join(context['temp_directory'],'tmp_4172.log'), 'w')
#  fn_nul = open(os.devnull, 'w')
#  subprocess.call( [ context['isql_path'], dsn, '-i', f_sql_chk.name], stdout = f_sql_log, stderr = fn_nul)
#
#  flush_and_close( f_sql_log )
#  fn_nul.close()
#
#  with open( f_sql_log.name,'r') as f:
#      for line in f:
#          if line.split():
#              print( ' '.join( line.split() ) )
#
#  # CLEANUP
#  #########
#  time.sleep(1)
#  cleanup( [i.name for i in (f_sql_chk, f_sql_log) ] )
#
#
#---

act_2 = python_act('db_2', substitutions=substitutions_2)

expected_stdout_2 = """
O_GDSCODE                       <null>
RDB$FUNCTION_NAME               THE_DIV
RDB$ENTRYPOINT                  unknown_udf!UC_div
RDB$ENGINE_NAME                 UDR
RDB$LEGACY_FLAG                 0
Records affected: 1
Records affected: 0

"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    test_script = """
    recreate view v_check as
    select rdb$function_name, rdb$entrypoint, rdb$engine_name, rdb$legacy_flag
    from rdb$functions
    where rdb$system_flag is distinct from 1 and rdb$function_name starting with upper( 'the_' )
    ;
    commit;

    set list on;
    set term ^;
    execute block returns( o_gdscode int ) as
    begin
        begin
            execute statement
              q'{
                    create function the_div (
                        n1 integer,
                        n2 integer
                    ) returns double precision
                        external name 'unknown_udf!UC_div'
                        engine udr
                }';
                -- was: external name 'udf_compat!UC_div'

        when any do
            begin
                o_gdscode = gdscode;
            end
        end
        suspend;
    end
    ^
    set term ;^

    commit;

    set blob all;
    set count on;

    select * from v_check;
    rollback;

    select * from v_check;
    rollback;
    """
    act_2.expected_stderr = 'We expect error, but ignore it'
    act_2.expected_stdout = expected_stdout_2
    act_2.isql(switches=[], input=test_script)
    assert act_2.clean_stdout == act_2.clean_expected_stdout

