#coding:utf-8
#
# id:           bugs.core_6248
# title:        A number of errors when database name is longer than 255 symbols
# decription:
#                   Test verifies that one may to create DB with total path plus name length L = 255 and 259 characters.
#                   Each DB is then subject for 'gbak -b', 'gbak -c', 'gstat -h', 'gfix -sweep' and 'gfix -v -full'.
#                   All these commands must NOT issue something to their STDERR.
#
#                   STDOUT-log of initial SQL must contain full DB name.
#                   Changed part of firebird.log for SWEEP and VALIDATION also must have full DB name (this is verified using regexp):
#                   +[tab]Database: C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\ABC.FDB // for validation
#                   +[tab]Database "C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\ABC.FDB // for sweep
#
#                   STDOUT-logs of backup, restore and gstat currently (09-mar-2020) have only truncated name (~235...241 chars).
#                   This may change in the future if FB developers will decide to fix this small inconveniences.
#
#                   For L=259 we must see in backup log following phrase:
#                       gbak:text for attribute 7 is too large in put_asciz(), truncating to 255 bytes
#                   - but currently this is not checked here.
#
#                   Checked on 4.0.0.1796.
#                   Checked on 4.0.0.2353: rdb$get_context('SYSTEM','DB_NAME') do not cut off full path and name to database
#                   and can return string with length = 32K, i.e. exceeding length of mon$database_name.
#                   See commit of 29-01-2021:
#                       https://github.com/FirebirdSQL/firebird/commit/d4835cab7f48288490ed83541132555c5cd0376d
#
# tracker_id:   CORE-6248
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
import re
import time
from difflib import unified_diff
from firebird.qa import db_factory, python_act, Action, Database
from firebird.driver import SrvRepairFlag

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """
    set list on;

    create exception exc_dbname_diff q'{Value in mon$database.mon$database_name differs from rdb$get_context('SYSTEM', 'DB_NAME'):@1@2@3=== vs ===@4@5}';
    set term ^;
    execute block returns(
         mon_database_column varchar(260)
        ,sys_context_db_name varchar(260)
    ) as
        declare lf char(1) = x'0A';
    begin
        select
            mon$database_name as mon_database_column
        from mon$database
        into mon_database_column;

        sys_context_db_name = rdb$get_context('SYSTEM', 'DB_NAME');

        if ( substring( sys_context_db_name from 1 for 255 ) is distinct from mon_database_column ) then
        begin
            exception exc_dbname_diff using(
                lf
                ,mon_database_column
                ,lf
                ,lf
                ,sys_context_db_name
            );
        end

        suspend;
    end
    ^
    set term ;^
    commit;
"""

db_1 = db_factory(sql_dialect=3)

# test_script_1
#---
#
#  import os
#  import sys
#  import tempfile
#  import difflib
#  import re
#  import time
#  import subprocess
#  from fdb import services
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  this_db = db_conn.database_name
#  db_conn.close()
#
#  #--------------------------------------------
#
#  def flush_and_close( file_handle ):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f,
#      # first do f.flush(), and
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb') and file_handle.name != os.devnull:
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#
#  #--------------------------------------------
#
#  def cleanup( f_names_list ):
#      global os
#      for f in f_names_list:
#         if type(f) == file:
#            del_name = f.name
#         elif type(f) == str:
#            del_name = f
#         else:
#            print('Unrecognized type of element:', f, ' - can not be treated as file.')
#            del_name = None
#
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#
#  #--------------------------------------------
#
#  def svc_get_fb_log( f_fb_log ):
#
#    global subprocess
#    subprocess.call([ context['fbsvcmgr_path'],
#                      "localhost:service_mgr",
#                      "action_get_fb_log"
#                    ],
#                     stdout=f_fb_log, stderr=subprocess.STDOUT
#                   )
#
#    return
#
#  #--------------------------------------------
#
#  def check_long_dbname(required_name_len, chars2fil):
#
#      global time, tempfile, subprocess, difflib
#      global flush_and_close, cleanup, svc_get_fb_log, re
#
#      MINIMAL_LEN_TO_SHOW=255
#      REDUCE_NAME_LEN_BY=0
#
#      folder = tempfile.gettempdir()
#      folder = context['temp_directory']
#      #folder = os.path.dirname(os.path.abspath(__file__))
#
#      f_name = ( chars2fil * 1000) [ : required_name_len - len(folder) - len('.fdb') - REDUCE_NAME_LEN_BY ] + '.fdb'
#
#      dbname = os.path.join( folder, f_name )
#
#      bkname = dbname[:-4] + '.fbk'
#
#      cleanup( (dbname,) )
#
#      sql_ddl='''        create database 'localhost:%(dbname)s';
#          set list on;
#
#          create exception exc_dbname_diff q'{Value in mon$database.mon$database_name differs from rdb$get_context('SYSTEM', 'DB_NAME'):@1@2@3=== vs ===@4@5}';
#          set term ^;
#          execute block returns(
#               mon_database_column varchar(260)
#              ,sys_context_db_name varchar(260)
#          ) as
#              declare lf char(1) = x'0A';
#          begin
#              select
#                  mon$database_name as mon_database_column
#              from mon$database
#              into mon_database_column;
#
#              sys_context_db_name = rdb$get_context('SYSTEM', 'DB_NAME');
#
#              if ( substring( sys_context_db_name from 1 for 255 ) is distinct from mon_database_column ) then
#              begin
#                  exception exc_dbname_diff using(
#                      lf
#                      ,mon_database_column
#                      ,lf
#                      ,lf
#                      ,sys_context_db_name
#                  );
#              end
#
#              suspend;
#          end
#          ^
#          set term ;^
#          commit;
#      ''' % locals()
#
#
#      f_sql_chk = open( os.path.join(context['temp_directory'],'tmp_6248_ddl.sql'), 'w')
#      f_sql_chk.write(sql_ddl)
#      flush_and_close( f_sql_chk )
#
#      ########################################################################
#
#      f_ddl_log = open( os.path.join(context['temp_directory'],'tmp_6248.ddl_'+str(required_name_len)+'.log'), 'w', buffering = 0)
#      f_ddl_err = open( ''.join( (os.path.splitext(f_sql_chk.name)[0], '.err' ) ), 'w', buffering = 0)
#
#      subprocess.call( [ context['isql_path'], '-q', '-i', f_sql_chk.name ], stdout = f_ddl_log, stderr = f_ddl_err)
#
#      flush_and_close( f_ddl_log )
#      flush_and_close( f_ddl_err )
#
#      ########################################################################
#
#      f_backup_log = open( os.path.join(context['temp_directory'],'tmp_6248.backup_'+str(required_name_len)+'.log'), 'w', buffering = 0)
#      f_backup_err = open( ''.join( (os.path.splitext(f_backup_log.name)[0], '.err' ) ), 'w', buffering = 0)
#
#      subprocess.call( [ context['gbak_path'], '-b', '-se', 'localhost:servce_mgr', dbname, bkname, '-v', '-st', 'tdrw' ], stdout = f_backup_log, stderr = f_backup_err)
#
#      flush_and_close( f_backup_log )
#      flush_and_close( f_backup_err )
#
#      ########################################################################
#
#      os.remove(dbname)
#
#      f_restore_log = open( os.path.join(context['temp_directory'],'tmp_6248.restore_'+str(required_name_len)+'.log'), 'w', buffering = 0)
#      f_restore_err = open( ''.join( (os.path.splitext(f_restore_log.name)[0], '.err' ) ), 'w', buffering = 0)
#
#      subprocess.call( [ context['gbak_path'], '-rep', '-se', 'localhost:servce_mgr', bkname, dbname, '-v', '-st', 'tdrw' ], stdout = f_restore_log, stderr = f_restore_err)
#
#      flush_and_close( f_restore_log )
#      flush_and_close( f_restore_err )
#
#      ########################################################################
#
#      f_gstat_log = open( os.path.join(context['temp_directory'],'tmp_6248.gstat_'+str(required_name_len)+'.log'), 'w', buffering = 0)
#      f_gstat_err = open( ''.join( (os.path.splitext(f_gstat_log.name)[0], '.err' ) ), 'w', buffering = 0)
#
#      subprocess.call( [ context['gstat_path'], '-h', 'localhost:' + dbname ], stdout = f_gstat_log, stderr = f_gstat_err)
#
#      flush_and_close( f_gstat_log )
#      flush_and_close( f_gstat_err )
#
#      ########################################################################
#
#      f_fblog_sweep_before = open( os.path.join(context['temp_directory'],'tmp_6248.fblog_before_sweep_'+str(required_name_len)+'.log'), 'w', buffering = 0)
#      svc_get_fb_log( f_fblog_sweep_before )
#      flush_and_close( f_fblog_sweep_before )
#
#      f_sweep_log = open( os.path.join(context['temp_directory'],'tmp_6248.sweep_'+str(required_name_len)+'.log'), 'w', buffering = 0)
#      f_sweep_err = open( ''.join( (os.path.splitext(f_sweep_log.name)[0], '.err' ) ), 'w', buffering = 0)
#
#      subprocess.call( [ context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_repair', 'dbname', dbname, 'rpr_sweep_db' ], stdout = f_sweep_log, stderr = f_sweep_err)
#
#      flush_and_close( f_sweep_log )
#      flush_and_close( f_sweep_err )
#
#      # Here we let firebird.log to be fulfilled with text about just finished SWEEP:
#      time.sleep(1)
#
#      f_fblog_sweep_after = open( os.path.join(context['temp_directory'],'tmp_6248.fblog_after_sweep_'+str(required_name_len)+'.log'), 'w', buffering = 0)
#      svc_get_fb_log( f_fblog_sweep_after )
#      flush_and_close( f_fblog_sweep_after )
#
#      oldfb=open(f_fblog_sweep_before.name, 'r')
#      newfb=open(f_fblog_sweep_after.name, 'r')
#
#      difftext = ''.join(difflib.unified_diff(
#          oldfb.readlines(),
#          newfb.readlines()
#        ))
#      oldfb.close()
#      newfb.close()
#
#      f_diff_sweep = open( os.path.join(context['temp_directory'],'tmp_6248.fblog_diff_sweep_'+str(required_name_len)+'.log'), 'w', buffering = 0)
#      f_diff_sweep.write(difftext)
#      flush_and_close( f_diff_sweep )
#
#      ########################################################################
#
#      f_fblog_validate_before = open( os.path.join(context['temp_directory'],'tmp_6248.fblog_before_validate_'+str(required_name_len)+'.log'), 'w', buffering = 0)
#      svc_get_fb_log( f_fblog_validate_before )
#      flush_and_close( f_fblog_validate_before )
#
#      f_valid_log = open( os.path.join(context['temp_directory'],'tmp_6248.valid_'+str(required_name_len)+'.log'), 'w', buffering = 0)
#      f_valid_err = open( ''.join( (os.path.splitext(f_valid_log.name)[0], '.err' ) ), 'w', buffering = 0)
#
#      subprocess.call( [ context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_repair', 'dbname', dbname, 'rpr_validate_db', 'rpr_full' ], stdout = f_valid_log, stderr = f_valid_err)
#
#      flush_and_close( f_valid_log )
#      flush_and_close( f_valid_err )
#
#      # Here we let firebird.log to be fulfilled with text about just finished VALIDATION:
#      time.sleep(1)
#
#      f_fblog_validate_after = open( os.path.join(context['temp_directory'],'tmp_6248.fblog_after_validate_'+str(required_name_len)+'.log'), 'w', buffering = 0)
#      svc_get_fb_log( f_fblog_validate_after )
#      flush_and_close( f_fblog_validate_after )
#
#
#      f_fblog_validate_after = open( os.path.join(context['temp_directory'],'tmp_6248.fblog_after_validate_'+str(required_name_len)+'.log'), 'w', buffering = 0)
#      svc_get_fb_log( f_fblog_validate_after )
#      flush_and_close( f_fblog_validate_after )
#
#      oldfb=open(f_fblog_validate_before.name, 'r')
#      newfb=open(f_fblog_validate_after.name, 'r')
#
#      difftext = ''.join(difflib.unified_diff(
#          oldfb.readlines(),
#          newfb.readlines()
#        ))
#      oldfb.close()
#      newfb.close()
#
#      f_diff_validate = open( os.path.join(context['temp_directory'],'tmp_6248.fblog_diff_validate_'+str(required_name_len)+'.log'), 'w', buffering = 0)
#      f_diff_validate.write(difftext)
#      flush_and_close( f_diff_validate )
#
#
#      ########################################################################
#
#      chk_list = (f_ddl_err, f_backup_err, f_restore_err, f_gstat_err, f_sweep_err, f_valid_err)
#      for c in chk_list:
#          with open(c.name,'r') as f:
#              for line in f:
#                  if line.split():
#                      print('UNEXPECTED ERROR, file:' + c.name +': ', line )
#
#      dbname_present_map = {}
#
#      # diff VALIDATION:
#      # +[tab]Database: C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\ABC.FDB
#      # diff SWEEP:
#      # +[tab]Database "C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\ABC.FDB
#      dbptrn = re.compile('\\+\\s+Database[:]{0,1}\\s+"{0,1}', re.IGNORECASE)
#
#      # STDOUT results: we have to check that AT LEAST 255 characters of database name present in log.
#      chk_list = (f_ddl_log, f_backup_log, f_restore_log, f_gstat_log, f_diff_sweep, f_diff_validate)
#      for c in chk_list:
#
#          # Name of STDOUT-log will serve as KEY for dbname_present_map{}, e.g.:
#          # C:\\FBTESTING\\qa\\fbt-repo\\tmp\\tmp_6248.backup_255.log  --> tmp_6248.backup_255
#          stdout_file = os.path.split( os.path.splitext( c.name )[0] )[1]
#
#          dbname_present_map[ stdout_file ] = 'DB NAME NOT FOUND'
#          with open(c.name,'r') as f:
#              for line in f:
#                  if c not in (f_diff_sweep, f_diff_validate) or line.startswith('+') and dbptrn.search(line):
#                      if dbname[:MINIMAL_LEN_TO_SHOW].upper() in line.upper():
#                          dbname_present_map[ stdout_file ] = 'found at least ' + str(MINIMAL_LEN_TO_SHOW)+' characters'
#                          break
#                      elif dbname[:128].upper() in line.upper():
#                          dbname_present_map[ stdout_file ] = 'found truncated DB name.'
#                          break
#
#      for k,v in sorted( dbname_present_map.items() ):
#          print(k, ':', v)
#
#      # Other STDOUT results will be analyzed after get developers resolution about
#      # truncation of DB names to ~235...241 characters.
#      # See notes of: 06/Mar/20 06:38 AM; 06/Mar/20 06:45 AM; 09/Mar/20 07:53 AM.
#      # Currently we do nothing and just remove them:
#
#      time.sleep(1)
#      cleanup( (f_sql_chk.name,  bkname, dbname, f_ddl_err, f_backup_err, f_restore_err, f_gstat_err, f_sweep_err, f_valid_err, f_ddl_log, f_backup_log, f_restore_log, f_gstat_log, f_sweep_log, f_valid_log, f_fblog_sweep_before, f_fblog_sweep_after, f_diff_sweep, f_fblog_validate_before, f_fblog_validate_after, f_diff_validate) )
#
#
#  #--------------------------------------------
#
#  check_long_dbname(255, 'abc255def')
#  check_long_dbname(259, 'qwe259rty')
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    ddl : found at least 255 characters
    backup : found truncated DB name.
    restore : found truncated DB name.
    gstat : found truncated DB name.
    fblog_diff_sweep : found at least 255 characters
    fblog_diff_validate : found at least 255 characters
"""

@pytest.fixture
def test_db(request: pytest.FixtureRequest, db_path) -> Database:
    required_name_len = request.param[0]
    chars2fil = request.param[1]
    filename = (chars2fil * 1000)[:required_name_len - len(str(db_path)) - 4] + '.fdb'
    db = Database(db_path, filename)
    db.create()
    yield db
    db.drop()

MINIMAL_LEN_TO_SHOW = 255

PATTERN = re.compile('\\+\\s+Database[:]{0,1}\\s+"{0,1}', re.IGNORECASE)

def check_filename_presence(lines, *, log_name: str, db: Database):
    filename = str(db.db_path) # To convert Path to string
    for line in lines:
        if log_name not in ('fblog_diff_sweep', 'fblog_diff_validate') or line.startswith('+') and PATTERN.search(line):
            if filename[:MINIMAL_LEN_TO_SHOW].upper() in line.upper():
                print(f'{log_name} : found at least {str(MINIMAL_LEN_TO_SHOW)} characters')
                return
            elif filename[:128].upper() in line.upper():
                print(f'{log_name} : found truncated DB name.')
                return
    print(f'{log_name} : DB NAME NOT FOUND')


@pytest.mark.version('>=4.0')
@pytest.mark.parametrize('test_db', [pytest.param((255, 'abc255def'), id='255'),
                                     pytest.param((259, 'qwe259rty'), id='259')], indirect=True)
def test_1(act_1: Action, test_db: Database, capsys):
    # INIT test
    act_1.isql(switches=['-q', test_db.dsn], input=init_script_1, connect_db=False)
    check_filename_presence(act_1.stdout.splitlines(), log_name='ddl', db=test_db)
    # GBAK BACKUP test
    backup_name = test_db.db_path.with_name(f"tmp_6248_backup_{len(test_db.db_path.with_suffix('').name)}.fbk")
    act_1.reset()
    act_1.gbak(switches=['-b', '-se', 'localhost:servce_mgr', '-v', '-st', 'tdwr', str(test_db.db_path), str(backup_name)])
    check_filename_presence(act_1.stdout.splitlines(), log_name='backup', db=test_db)
    # GBAK RESTORE test
    act_1.reset()
    act_1.gbak(switches=['-rep', '-se', 'localhost:servce_mgr', '-v', '-st', 'tdwr', str(backup_name), str(test_db.db_path)])
    check_filename_presence(act_1.stdout.splitlines(), log_name='restore', db=test_db)
    # GSTAT test
    act_1.reset()
    act_1.gstat(switches=['-h', test_db.dsn], connect_db=False)
    check_filename_presence(act_1.stdout.splitlines(), log_name='gstat', db=test_db)
    # SWEEP test
    log_before = act_1.get_firebird_log()
    with act_1.connect_server() as srv:
        srv.database.sweep(database=test_db.db_path)
    time.sleep(1) # Let firebird.log to be fulfilled with text about just finished SWEEP
    log_after = act_1.get_firebird_log()
    check_filename_presence(list(unified_diff(log_before, log_after)), log_name='fblog_diff_sweep', db=test_db)
    # VALIDATE test
    log_before = act_1.get_firebird_log()
    with act_1.connect_server() as srv:
        srv.database.repair(database=test_db.db_path, flags=SrvRepairFlag.FULL | SrvRepairFlag.VALIDATE_DB)
    time.sleep(1) # Let firebird.log to be fulfilled with text about just finished VALIDATION
    log_after = act_1.get_firebird_log()
    check_filename_presence(list(unified_diff(log_before, log_after)), log_name='fblog_diff_validate', db=test_db)
    # Check
    act_1.reset()
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
