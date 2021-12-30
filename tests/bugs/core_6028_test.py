#coding:utf-8
#
# id:           bugs.core_6028
# title:        Trigger on system table restored in FB3 database and can't be deleted
# decription:
#                   We restore here database that was created in FB 2.5.9 and contained triggers for tables RDB$RELATION_FIELDS, MON$STATEMENTS and MON$ATTACHMENTS.
#                   Table RDB$RELATION_FIELDS had triggers BEFORE INSERT and AFTER INSERT. Monitoring tabled had triggers BEFORE DELETE and AFTER DELETE.
#                   Also, table 'TLOG' is in this database, and this table serves as log for actions: create/drop table; delete from mon$statements and delete from mon$attachments.
#                   For DDL like 'create table test(x int)' and 'drop table test' table TLOG will contain two records which are added there by triggers on RDB$RELATION_FIELDS.
#                   Further, if we create addition connection and run statement which returns at least one record (like 'select ... from rdb$database') then in 2.5 two recors
#                   had been added into TLOG for each of: 'DELETE FROM MON$STATEMENTS' and 'DELETE FROM MON$ATTACHMENTS'.
#
#                   Finally, BEFORE fix of this ticket issue (e.g. in WI-V3.0.5.33109):
#                   1) restored database contained following triggers: TRG_MON_ATTACHMENTS*, TRG_MON_STATEMENTS* and TRG_RDB_REL_FIELDS*
#                   2) statements 'create table' and 'drop table' led to logging following records in TLOG:
#                         rdb$relation_fields: record is to be created
#                         rdb$relation_fields: record has been created
#                         rdb$relation_fields: record is to be removed
#                         rdb$relation_fields: record has been removed
#                   3) command 'delete from mon$statement' (when there was another non-system connection with one running or completed statement)
#                      led to logging these records in TLOG:
#                         mon$statements: record is to be removed
#                         mon$statements: record has been removed
#                   4) command 'delete from mon$attachments' (when there was another non-system connection) led to logging these records in TLOG:
#                         mon$attachments: record is to be removed
#                         mon$attachments: record has been removed
#
#                   All of above mentioned should NOT appear in a database that is restored AFTER this ticket was fixed.
#                   Finally, we try to create three new triggers for tables rdb$relation-fields, mon$statements and mon$attachments.
#                   All of these attempts must FAIL with:
#                   ========
#                       - no permission for ALTER access to TABLE RDB$RELATION_FIELDS
#                       -607
#                       335544351
#                   ========
#                   Ticket issue confirmed on: 3.0.5.33109
#                   Checked on 3.0.5.33115: OK, 3.721s.
#
# tracker_id:   CORE-6028
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
import zipfile
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file, Database
from firebird.driver import SrvRestoreFlag, DatabaseError

# version: 3.0.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)
db_1_tmp = db_factory(sql_dialect=3, filename='tmp_core_602.fdb', do_not_create=True)

# test_script_1
#---
#
#  import os
#  import fdb
#  import time
#  import zipfile
#  import difflib
#  import subprocess
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
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
#  zf = zipfile.ZipFile( os.path.join(context['files_location'],'core_6028_25.zip') )
#  tmpfbk = 'core_6028_25.fbk'
#  zf.extract( tmpfbk, '$(DATABASE_LOCATION)')
#  zf.close()
#
#  tmpfbk='$(DATABASE_LOCATION)'+tmpfbk
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_core_6028.fdb'
#
#  f_restore_log=open( os.path.join(context['temp_directory'],'tmp_core_6028_restore.log'), 'w')
#  subprocess.check_call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                         "action_restore",
#                         "bkp_file", tmpfbk,
#                         "dbname", tmpfdb,
#                         "res_replace",
#                         "verbose"
#                        ],
#                        stdout=f_restore_log,
#                        stderr=subprocess.STDOUT)
#  flush_and_close( f_restore_log )
#
#  # https://pythonhosted.org/fdb/reference.html#fdb.Cursor
#
#  con_worker=fdb.connect(dsn = 'localhost:'+tmpfdb)
#  con_worker_attachment_id = con_worker.attachment_id
#
#  con_worker.execute_immediate( 'create table test(id int)' )
#  con_worker.commit()
#  con_worker.execute_immediate( 'drop table test' )
#  con_worker.commit()
#
#  cur_worker=con_worker.cursor()
#  cur_worker.execute( "select coalesce(rt.rdb$trigger_name, 'NO USER-DEFINED TRIGGERS IN JUST RESTORED DATABASE.') from rdb$database rd left join rdb$triggers rt on rt.rdb$system_flag is distinct from 1 order by 1" )
#  for r in cur_worker:
#      print( r[0] )
#
#  con_killer=fdb.connect(dsn = 'localhost:'+tmpfdb)
#  cur_killer=con_killer.cursor()
#
#  cur_killer.execute( 'delete from mon$statements s where s.mon$attachment_id = %d' % con_worker_attachment_id )
#  con_killer.commit()
#
#  cur_killer.execute( 'delete from mon$attachments a where a.mon$attachment_id = %d' % con_worker_attachment_id )
#  con_killer.commit()
#
#  cur_killer.execute( "select coalesce(t.action, 'NO ACTIONS WAS LOGGED IN THE TABLE TLOG.') as sys_tabs_action from rdb$database rd left join tlog t on 1=1" )
#  for r in cur_killer:
#      print( r[0] )
#
#  try:
#      cur_worker.close()
#      con_worker.close()
#  except Exception,e:
#      pass
#
#  #-----------------------
#
#  ddl_probes=[]
#
#  ddl_probes.append(
#  '''
#      create or alter trigger new_trg_rdb_rel_flds_bi for rdb$relation_fields active before insert position 0 as
#      begin
#         insert into tlog(id, action) values( gen_id(g, 111), 'rdb$relation_fields: record is to be created' );
#      end
#  '''
#  )
#
#  ddl_probes.append(
#  '''
#      create or alter trigger new_trg_mon_stm_bd for mon$statements active before delete position 0 as
#      begin
#         insert into tlog(id, action) values( gen_id(g, 222), 'mon$statements: record is to be removed' );
#      end
#  '''
#  )
#
#  ddl_probes.append(
#  '''
#      create or alter trigger new_trg_mon_att_bd for mon$attachments active before delete position 0 as
#      begin
#         insert into tlog(id, action) values( gen_id(g, 333), 'mon$attachments: record is to be removed' );
#      end
#  '''
#  )
#
#  for s in ddl_probes:
#      try:
#          con_killer.execute_immediate( s )
#      except Exception,e:
#          print( e[0].split('\\n')[-1] ) # Get last substring from error message: "- no permission for ALTER access to TABLE RDB$RELATION_FIELDS"
#          print( e[1] ) # SQLCODE: -607
#          print( e[2] ) # gdscode: 335544351L
#
#  #-----------------------
#
#  cur_killer.close()
#  con_killer.close()
#
#
#  # Cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (tmpfbk, tmpfdb, f_restore_log) )
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    NO USER-DEFINED TRIGGERS IN JUST RESTORED DATABASE.
    NO ACTIONS WAS LOGGED IN THE TABLE TLOG.
    unsuccessful metadata update
    -CREATE OR ALTER TRIGGER NEW_TRG_RDB_REL_FLDS_BI failed
    -no permission for ALTER access to TABLE RDB$RELATION_FIELDS
    -607
    (335544351, 336397272, 335544352)
    unsuccessful metadata update
    -CREATE OR ALTER TRIGGER NEW_TRG_MON_STM_BD failed
    -no permission for ALTER access to TABLE MON$STATEMENTS
    -607
    (335544351, 336397272, 335544352)
    unsuccessful metadata update
    -CREATE OR ALTER TRIGGER NEW_TRG_MON_ATT_BD failed
    -no permission for ALTER access to TABLE MON$ATTACHMENTS
    -607
    (335544351, 336397272, 335544352)
"""

fbk_file_1 = temp_file('core_6028_25.fbk')

ddl_probes = ["""
    create or alter trigger new_trg_rdb_rel_flds_bi for rdb$relation_fields active before insert position 0 as
    begin
       insert into tlog(id, action) values( gen_id(g, 111), 'rdb$relation_fields: record is to be created' );
    end
    """, """
    create or alter trigger new_trg_mon_stm_bd for mon$statements active before delete position 0 as
    begin
       insert into tlog(id, action) values( gen_id(g, 222), 'mon$statements: record is to be removed' );
    end
    """, """
    create or alter trigger new_trg_mon_att_bd for mon$attachments active before delete position 0 as
    begin
       insert into tlog(id, action) values( gen_id(g, 333), 'mon$attachments: record is to be removed' );
    end
    """]

@pytest.mark.version('>=3.0.5')
def test_1(act_1: Action, fbk_file_1: Path, db_1_tmp: Database, capsys):
    zipped_fbk_file = zipfile.Path(act_1.files_dir / 'core_6028_25.zip',
                                   at='core_6028_25.fbk')
    fbk_file_1.write_bytes(zipped_fbk_file.read_bytes())
    #
    with act_1.connect_server() as srv:
        srv.database.restore(backup=fbk_file_1, database=db_1_tmp.db_path,
                             flags=SrvRestoreFlag.REPLACE)
        srv.wait()
    #
    con_worker = db_1_tmp.connect()
    con_worker_attachment_id = con_worker.info.id
    con_worker.execute_immediate('create table test(id int)')
    con_worker.commit()
    con_worker.execute_immediate('drop table test')
    con_worker.commit()
    #
    cur_worker=con_worker.cursor()
    cur_worker.execute("select coalesce(rt.rdb$trigger_name, 'NO USER-DEFINED TRIGGERS IN JUST RESTORED DATABASE.') from rdb$database rd left join rdb$triggers rt on rt.rdb$system_flag is distinct from 1 order by 1")
    for r in cur_worker:
        print(r[0])
    #
    with db_1_tmp.connect() as con_killer:
        cur_killer = con_killer.cursor()
        cur_killer.execute(f'delete from mon$statements s where s.mon$attachment_id = {con_worker_attachment_id}')
        con_killer.commit()
        cur_killer.execute(f'delete from mon$attachments a where a.mon$attachment_id = {con_worker_attachment_id}')
        con_killer.commit()
        cur_killer.execute("select coalesce(t.action, 'NO ACTIONS WAS LOGGED IN THE TABLE TLOG.') as sys_tabs_action from rdb$database rd left join tlog t on 1=1")
        for r in cur_killer:
            print(r[0])
        #
        try:
            cur_worker.close()
        except Exception:
            pass
        try:
            con_worker.close()
        except Exception:
            pass
        #
        for cmd in ddl_probes:
            try:
                con_killer.execute_immediate(cmd)
            except DatabaseError as e:
                print(e)
                print(e.sqlcode)
                print(e.gds_codes)
    # Check
    act_1.reset()
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
