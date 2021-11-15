#coding:utf-8
#
# id:           bugs.core_2251
# title:        gbak doesn't return error code
# decription:
#                   Inaccessible folder is defined here as $tmp + GUID (i.e. it 100% not yet exists).
#                   We have to check allof kind for inaccessible file:
#                       * .fbk when trying to make backup of existing database;
#                       * .fdb when trying to restore from existing .fbk;
#                       * .log - for any of these operation
#                   We are NOT interested when all of these files are in accessible folder(s).
#
#                   Query to obtain set of interested combinations (all of them should have retcode = 1):
#                       with
#                       a as (
#                           select 'backup' as action from rdb$database union all
#                           select 'restore' from rdb$database
#                       )
#                       ,s as (
#                           select 'inaccessible' as path_to_source_file from rdb$database union all
#                           select 'accessible' from rdb$database
#                       )
#                       ,t as (
#                           select 'inaccessible' as path_to_target_file from rdb$database union all
#                           select 'accessible' from rdb$database
#                       )
#                       ,g as (
#                           select 'inaccessible' as path_to_action_log from rdb$database union all
#                           select 'accessible' from rdb$database
#                       )
#                       select * from a,s,t,g
#                       where NOT (s.path_to_source_file = 'accessible' and t.path_to_target_file = 'accessible' and g.path_to_action_log = 'accessible')
#                       order by 1,2,3,4;
#
#                   Confirmed wrong results on: 4.0.0.1714 SC; 4.0.0.1715 CS;  3.0.5.33221 SC; 3.0.5.33225 CS
#                   Checked on:
#                       4.0.0.1726 SS: 3.759s.
#                       3.0.5.33232 SS: 1.671s.
#
# tracker_id:   CORE-2251
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
import subprocess
from uuid import uuid4
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file

# version: 3.0.5
# resources: None

substitutions_1 = [('\t+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import sys
#  import uuid
#  import subprocess
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  correct_fdb=db_conn.database_name
#  db_conn.close()
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
#  inaccessible_dir = os.path.join(context['temp_directory'], str(uuid.uuid4()) )
#
#  invalid_fdb=os.path.join(inaccessible_dir,'tmp_2251.fdb')
#
#  invalid_fbk=os.path.join(inaccessible_dir,'tmp_2251.fbk')
#  correct_fbk=os.path.join(context['temp_directory'],'tmp_2251.fbk')
#
#  invalid_res=os.path.join(inaccessible_dir,'tmp_2251.tmp')
#  correct_res=os.path.join(context['temp_directory'],'tmp_2251.tmp')
#
#  invalid_log=os.path.join(inaccessible_dir,'tmp_2251.log')
#  correct_log=os.path.join(context['temp_directory'],'tmp_2251.log')
#
#  ##########################################################################################
#
#  f_null_log = open(os.devnull,"w")
#  gbak_retcode = subprocess.call( [context['gbak_path'], '-b', '-se', 'localhost:service_mgr', correct_fdb, correct_fbk, '-y', invalid_log ], stdout=f_null_log, stderr=subprocess.STDOUT)
#  print( 'backup  source_fdb=accessible          target_fbk=accessible          log_file=inaccessible:'.ljust(100), gbak_retcode )
#
#  cleanup( (correct_log,) )
#  gbak_retcode = subprocess.call( [context['gbak_path'], '-b', '-se', 'localhost:service_mgr', correct_fdb, invalid_fbk, '-y', correct_log ], stdout=f_null_log, stderr=subprocess.STDOUT)
#  print('backup  source_fdb=accessible          target_fbk=inaccessible        log_file=accessible:'.ljust(100), gbak_retcode)
#
#  gbak_retcode = subprocess.call( [context['gbak_path'], '-b', '-se', 'localhost:service_mgr', correct_fdb, invalid_fbk, '-y', invalid_log ], stdout=f_null_log, stderr=subprocess.STDOUT)
#  print('backup  source_fdb=accessible          target_fbk=inaccessible        log_file=inaccessible:'.ljust(100), gbak_retcode)
#
#  cleanup( (correct_log,) )
#  gbak_retcode = subprocess.call( [context['gbak_path'], '-b', '-se', 'localhost:service_mgr', invalid_fdb, correct_fbk, '-y', correct_log ], stdout=f_null_log, stderr=subprocess.STDOUT)
#  print('backup  source_fdb=inaccessible        target_fbk=accessible          log_file=accessible:'.ljust(100), gbak_retcode)
#
#  gbak_retcode = subprocess.call( [context['gbak_path'], '-b', '-se', 'localhost:service_mgr', invalid_fdb, correct_fbk, '-y', invalid_log ], stdout=f_null_log, stderr=subprocess.STDOUT)
#  print('backup  source_fdb=inaccessible        target_fbk=accessible          log_file=inaccessible:'.ljust(100), gbak_retcode)
#
#  cleanup( (correct_log,) )
#  gbak_retcode = subprocess.call( [context['gbak_path'], '-b', '-se', 'localhost:service_mgr', invalid_fdb, invalid_fbk, '-y', correct_log ], stdout=f_null_log, stderr=subprocess.STDOUT)
#  print('backup  source_fdb=inaccessible        target_fbk=inaccessible        log_file=accessible:'.ljust(100), gbak_retcode)
#
#  gbak_retcode = subprocess.call( [context['gbak_path'], '-b', '-se', 'localhost:service_mgr', invalid_fdb, invalid_fbk, '-y', invalid_log ], stdout=f_null_log, stderr=subprocess.STDOUT)
#  print('backup  source_fdb=inaccessible        target_fbk=inaccessible        log_file=inaccessible:'.ljust(100), gbak_retcode)
#
#  ######################################################################################
#  runProgram('gbak', [ '-b', '-se', 'localhost:service_mgr', correct_fdb, correct_fbk] )
#  ######################################################################################
#
#  gbak_retcode = subprocess.call( [context['gbak_path'], '-rep', '-se', 'localhost:service_mgr', correct_fbk, correct_fdb, '-y', invalid_log ], stdout=f_null_log, stderr=subprocess.STDOUT)
#  print( 'restore source_fbk=accessible          target_fdb=accessible          log_file=inaccessible:'.ljust(100), gbak_retcode )
#
#  cleanup( (correct_log,) )
#  gbak_retcode = subprocess.call( [context['gbak_path'], '-rep', '-se', 'localhost:service_mgr', correct_fbk, invalid_fdb, '-y', correct_log ], stdout=f_null_log, stderr=subprocess.STDOUT)
#  print( 'restore source_fbk=accessible          target_fdb=inaccessible        log_file=accessible:'.ljust(100), gbak_retcode )
#
#  gbak_retcode = subprocess.call( [context['gbak_path'], '-rep', '-se', 'localhost:service_mgr', correct_fbk, invalid_fdb, '-y', invalid_log ], stdout=f_null_log, stderr=subprocess.STDOUT)
#  print( 'restore source_fbk=accessible          target_fdb=inaccessible        log_file=inaccessible:'.ljust(100), gbak_retcode )
#
#  cleanup( (correct_log,) )
#  gbak_retcode = subprocess.call( [context['gbak_path'], '-rep', '-se', 'localhost:service_mgr', invalid_fbk, correct_fdb, '-y', correct_log ], stdout=f_null_log, stderr=subprocess.STDOUT)
#  print( 'restore source_fbk=inaccessible        target_fdb=accessible          log_file=accessible:'.ljust(100), gbak_retcode )
#
#  gbak_retcode = subprocess.call( [context['gbak_path'], '-rep', '-se', 'localhost:service_mgr', invalid_fbk, correct_fdb, '-y', invalid_log ], stdout=f_null_log, stderr=subprocess.STDOUT)
#  print( 'restore source_fbk=inaccessible        target_fdb=accessible          log_file=inaccessible:'.ljust(100), gbak_retcode )
#
#  cleanup( (correct_log,) )
#  gbak_retcode = subprocess.call( [context['gbak_path'], '-rep', '-se', 'localhost:service_mgr', invalid_fbk, invalid_fdb, '-y', correct_log ], stdout=f_null_log, stderr=subprocess.STDOUT)
#  print( 'restore source_fbk=inaccessible        target_fdb=inaccessible        log_file=accessible:'.ljust(100), gbak_retcode )
#
#  gbak_retcode = subprocess.call( [context['gbak_path'], '-rep', '-se', 'localhost:service_mgr', invalid_fbk, invalid_fdb, '-y', invalid_log ], stdout=f_null_log, stderr=subprocess.STDOUT)
#  print( 'restore source_fbk=inaccessible        target_fdb=inaccessible        log_file=inaccessible:'.ljust(100), gbak_retcode )
#
#  f_null_log.close()
#
#  cleanup( (correct_log,correct_fbk,) )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    backup  source_fdb=accessible          target_fbk=accessible          log_file=inaccessible:         1
    backup  source_fdb=accessible          target_fbk=inaccessible        log_file=accessible:           1
    backup  source_fdb=accessible          target_fbk=inaccessible        log_file=inaccessible:         1
    backup  source_fdb=inaccessible        target_fbk=accessible          log_file=accessible:           1
    backup  source_fdb=inaccessible        target_fbk=accessible          log_file=inaccessible:         1
    backup  source_fdb=inaccessible        target_fbk=inaccessible        log_file=accessible:           1
    backup  source_fdb=inaccessible        target_fbk=inaccessible        log_file=inaccessible:         1
    restore source_fbk=accessible          target_fdb=accessible          log_file=inaccessible:         1
    restore source_fbk=accessible          target_fdb=inaccessible        log_file=accessible:           1
    restore source_fbk=accessible          target_fdb=inaccessible        log_file=inaccessible:         1
    restore source_fbk=inaccessible        target_fdb=accessible          log_file=accessible:           1
    restore source_fbk=inaccessible        target_fdb=accessible          log_file=inaccessible:         1
    restore source_fbk=inaccessible        target_fdb=inaccessible        log_file=accessible:           1
    restore source_fbk=inaccessible        target_fdb=inaccessible        log_file=inaccessible:         1
  """

inaccessible_dir = temp_file(uuid4().hex)
correct_fbk = temp_file('tmp_2251.fbk')
correct_res = temp_file('tmp_2251.tmp')
correct_log = temp_file('tmp_2251.log')

@pytest.mark.version('>=3.0.5')
def test_1(act_1: Action, capsys, inaccessible_dir: Path, correct_fbk: Path,
           correct_res: Path, correct_log: Path):
    correct_fdb = act_1.db.db_path
    invalid_fdb = inaccessible_dir / 'tmp_2251.fdb'
    invalid_fbk = inaccessible_dir / 'tmp_2251.fbk'
    #invalid_res = inaccessible_dir / 'tmp_2251.tmp'
    invalid_log = inaccessible_dir / 'tmp_2251.log'
    #
    gbak_retcode = subprocess.call( [act_1.vars['gbak'], '-b', '-se', 'localhost:service_mgr',
                                     correct_fdb, correct_fbk, '-y', invalid_log ],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print( 'backup  source_fdb=accessible          target_fbk=accessible          log_file=inaccessible:'.ljust(100), gbak_retcode )

    gbak_retcode = subprocess.call( [act_1.vars['gbak'], '-b', '-se', 'localhost:service_mgr',
                                     correct_fdb, invalid_fbk, '-y', correct_log ],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print('backup  source_fdb=accessible          target_fbk=inaccessible        log_file=accessible:'.ljust(100), gbak_retcode)

    gbak_retcode = subprocess.call( [act_1.vars['gbak'], '-b', '-se', 'localhost:service_mgr',
                                     correct_fdb, invalid_fbk, '-y', invalid_log ],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print('backup  source_fdb=accessible          target_fbk=inaccessible        log_file=inaccessible:'.ljust(100), gbak_retcode)

    gbak_retcode = subprocess.call( [act_1.vars['gbak'], '-b', '-se', 'localhost:service_mgr',
                                     invalid_fdb, correct_fbk, '-y', correct_log ],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print('backup  source_fdb=inaccessible        target_fbk=accessible          log_file=accessible:'.ljust(100), gbak_retcode)

    gbak_retcode = subprocess.call( [act_1.vars['gbak'], '-b', '-se', 'localhost:service_mgr',
                                     invalid_fdb, correct_fbk, '-y', invalid_log ],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print('backup  source_fdb=inaccessible        target_fbk=accessible          log_file=inaccessible:'.ljust(100), gbak_retcode)

    gbak_retcode = subprocess.call( [act_1.vars['gbak'], '-b', '-se', 'localhost:service_mgr',
                                     invalid_fdb, invalid_fbk, '-y', correct_log ],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print('backup  source_fdb=inaccessible        target_fbk=inaccessible        log_file=accessible:'.ljust(100), gbak_retcode)

    gbak_retcode = subprocess.call( [act_1.vars['gbak'], '-b', '-se', 'localhost:service_mgr',
                                     invalid_fdb, invalid_fbk, '-y', invalid_log ],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print('backup  source_fdb=inaccessible        target_fbk=inaccessible        log_file=inaccessible:'.ljust(100), gbak_retcode)

    ######################################################################################
    act_1.gbak(switches=['-b', '-se', 'localhost:service_mgr', correct_fdb, correct_fbk] )
    ######################################################################################

    gbak_retcode = subprocess.call( [act_1.vars['gbak'], '-rep', '-se', 'localhost:service_mgr',
                                     correct_fbk, correct_fdb, '-y', invalid_log ],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print( 'restore source_fbk=accessible          target_fdb=accessible          log_file=inaccessible:'.ljust(100), gbak_retcode )

    gbak_retcode = subprocess.call( [act_1.vars['gbak'], '-rep', '-se', 'localhost:service_mgr',
                                     correct_fbk, invalid_fdb, '-y', correct_log ],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print( 'restore source_fbk=accessible          target_fdb=inaccessible        log_file=accessible:'.ljust(100), gbak_retcode )

    gbak_retcode = subprocess.call( [act_1.vars['gbak'], '-rep', '-se', 'localhost:service_mgr',
                                     correct_fbk, invalid_fdb, '-y', invalid_log ],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print( 'restore source_fbk=accessible          target_fdb=inaccessible        log_file=inaccessible:'.ljust(100), gbak_retcode )

    gbak_retcode = subprocess.call( [act_1.vars['gbak'], '-rep', '-se', 'localhost:service_mgr',
                                     invalid_fbk, correct_fdb, '-y', correct_log ],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print( 'restore source_fbk=inaccessible        target_fdb=accessible          log_file=accessible:'.ljust(100), gbak_retcode )

    gbak_retcode = subprocess.call( [act_1.vars['gbak'], '-rep', '-se', 'localhost:service_mgr',
                                     invalid_fbk, correct_fdb, '-y', invalid_log ],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print( 'restore source_fbk=inaccessible        target_fdb=accessible          log_file=inaccessible:'.ljust(100), gbak_retcode )

    gbak_retcode = subprocess.call( [act_1.vars['gbak'], '-rep', '-se', 'localhost:service_mgr',
                                     invalid_fbk, invalid_fdb, '-y', correct_log ],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print( 'restore source_fbk=inaccessible        target_fdb=inaccessible        log_file=accessible:'.ljust(100), gbak_retcode )

    gbak_retcode = subprocess.call( [act_1.vars['gbak'], '-rep', '-se', 'localhost:service_mgr',
                                     invalid_fbk, invalid_fdb, '-y', invalid_log ],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print( 'restore source_fbk=inaccessible        target_fdb=inaccessible        log_file=inaccessible:'.ljust(100), gbak_retcode )
    #
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout

