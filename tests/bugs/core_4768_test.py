#coding:utf-8
#
# id:           bugs.core_4768
# title:        CREATE USER ... TAGS ( argument_1 = 'value1', ..., argument_N = 'valueN' ) - wrong results of statement when there are many arguments
# decription:
#                   Checked on:
#                       FB30SS, build 3.0.4.32985: OK, 7.672s.
#                       FB40SS, build 4.0.0.1000: OK, 13.094s.
#
# tracker_id:   CORE-4768
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action, user_factory, User

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import subprocess
#  import time
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  #--------------------------------------------
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
#
#  #--------------------------------------------
#
#
#  TAGS_COUNT=100000
#  #^^^^^^^^^^^^^^^^--- TAGS COUNT: THRESHOLD
#
#  f_chk_sql=open( os.path.join(context['temp_directory'],'tmp_tags_4768.sql'), 'w')
#  f_chk_sql.write('set bail on;\\n')
#  f_chk_sql.write("create or alter user tmp$c4768_1 password '123' using plugin Srp tags (\\n")
#
#  for i in range(0,TAGS_COUNT):
#      f_chk_sql.write( ('  ,' if i>0 else '  ') + 'arg_'+str(i)+"='val"+str(i)+"'\\n" )
#  f_chk_sql.write(');\\n')
#  f_chk_sql.write('commit;\\n')
#
#  sql_check='''set count on;
#  set list on;
#  select
#       u.sec$user_name as usr_name
#      ,u.sec$plugin sec_plugin
#      ,upper(min( a.sec$key )) tag_min
#      ,upper(min( a.sec$value )) val_min
#      ,upper(max( a.sec$key )) tag_max
#      ,upper(max( a.sec$value )) val_max
#      ,count(*) tag_cnt
#  from sec$users u
#  left join sec$user_attributes a on u.sec$user_name = a.sec$user_name
#  where u.sec$user_name = upper('tmp$c4768_1')
#  group by 1,2
#  ;
#  commit;
#  drop user tmp$c4768_1 using plugin Srp;
#  commit;
#  '''
#
#  f_chk_sql.write(sql_check)
#  f_chk_sql.write('commit;\\n')
#
#  flush_and_close( f_chk_sql )
#
#
#  f_tags_log = open( os.path.join(context['temp_directory'],'tmp_tags_4768.log'), 'w')
#  f_tags_err = open( os.path.join(context['temp_directory'],'tmp_tags_4768.err'), 'w')
#
#  subprocess.call( [ context['isql_path'], dsn, "-q", "-i", f_chk_sql.name],
#                   stdout = f_tags_log,
#                   stderr = f_tags_err
#                 )
#
#  flush_and_close( f_tags_log )
#  flush_and_close( f_tags_err )
#
#  with open(f_tags_log.name) as f:
#      for line in f:
#          print(line)
#
#  with open(f_tags_err.name) as f:
#      for line in f:
#          print('UNEXPECTED STDERR: ' + line)
#
#  # CLEANUP:
#  ##########
#  time.sleep(1)
#  cleanup( [i.name for i in ( f_chk_sql, f_tags_log, f_tags_err ) ] )
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
        USR_NAME                        TMP$C4768_1
        SEC_PLUGIN                      Srp
        TAG_MIN                         ARG_0
        VAL_MIN                         VAL0
        TAG_MAX                         ARG_99999
        VAL_MAX                         VAL99999
        TAG_CNT                         100000
        Records affected: 1
"""

# Cleanup fixture
user_1 = user_factory('db_1', name='tmp$c4768_1', password='123', plugin='Srp',
                      do_not_create=True)

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, user_1: User):
    TAGS_COUNT = 100000
    check_lines = ['set bail on;',
                   "create or alter user tmp$c4768_1 password '123' using plugin Srp tags ("]
    for i in range(TAGS_COUNT):
        check_lines.append(f"{'  ,' if i > 0 else '  '}arg_{i}='val{i}'")
    check_lines.append(');')
    check_lines.append('commit;')
    test_script = '\n'.join(check_lines) + """
    set count on;
    set list on;
    select
         u.sec$user_name as usr_name
        ,u.sec$plugin sec_plugin
        ,upper(min( a.sec$key )) tag_min
        ,upper(min( a.sec$value )) val_min
        ,upper(max( a.sec$key )) tag_max
        ,upper(max( a.sec$value )) val_max
        ,count(*) tag_cnt
    from sec$users u
    left join sec$user_attributes a on u.sec$user_name = a.sec$user_name
    where u.sec$user_name = upper('tmp$c4768_1')
    group by 1,2 ;
    commit;
    """
    act_1.expected_stdout = expected_stdout_1
    act_1 .isql(switches=['-q'], input=test_script)
    assert act_1.clean_stdout == act_1.clean_expected_stdout
