#coding:utf-8
#
# id:           bugs.core_6182
# title:        ExtConnPoolLifeTime acts as countdown for activity in MOST RECENT database (of several) rather then separate for each of used databases
# decription:
#                   We create one main ('head') DB (only for make single attach to it) and four test databases for making EDS connections to each of them from main DB.
#                   Special user is created using LEGACY plugin because of comment in the ticket by hvlad 06/Nov/19 01:36 PM.
#                                                 ~~~~~~
#                   Then we do subsequent connections to each of these databases using EDS mechanism, with delay between them (and also with final delay).
#                   Total sum of seconds that execution was paused is 4 * TDELAY - must be GREATER than config parameter ExtConnPoolLifeTime.
#                   After last delay will elapsed, we again establish connections to each of these databases and try to execute DROP DATABASE statements.
#
#                   Main idea: FIRST of this databases (which was firstly used to EDS connection) must have NO any attachments in its ExtPool and DROP must pass w/o any problems.
#
#                   ::: NOTE ::: ATTENTION ::: ACHTUNG :::
#
#                   We can not issue 'DROP DATABASE' immediately becase if some connection remains in ExtPool then FDB will raise exception that can not be catched.
#                   For this reason we have to kill all attachments using 'DELETE FROM MON$ATTACHMENTS' statement. Number of attachments that were deleted will show
#                   whether there was some 'auxiliary' connections or not. For the first of checked databases this number must be 0 (zero).
#                   Otherwise one can state that the problem with ExtPool still exists.
#
#                   Checked on:
#                       4.0.0.1646 SS/SC: ~19s (most of time is idle because of delays that is necessary for check that connections disappeared from ExtPool)
#                       4.0.0.1646 CS: 21.339s - but this test is not needed for this acrh.
#
# tracker_id:   CORE-6182
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
import time
from firebird.qa import db_factory, python_act, Action, user_factory, User, Database

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1, filename='core_6182-main.fdb')
db_1_a = db_factory(sql_dialect=3, init=init_script_1, filename='core_6182-1.fdb')
db_1_b = db_factory(sql_dialect=3, init=init_script_1, filename='core_6182-2.fdb')
db_1_c = db_factory(sql_dialect=3, init=init_script_1, filename='core_6182-3.fdb')
db_1_d = db_factory(sql_dialect=3, init=init_script_1, filename='core_6182-4.fdb')


# test_script_1
#---
#
#  import os
#  import sys
#  import time
#  import subprocess
#  import fdb
#  from fdb import services
#
#  DB_PATH = context['temp_directory']
#  # os.sep.join( db_conn.database_name.split(os.sep)[:-1] )
#
#  DB_USER=user_name
#  DB_PSWD=user_password
#
#  EDS_USER='tmp$c6182_leg'
#  EDS_PSWD='123'
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
#  TDELAY=3
#  DB_CNT=4
#
#  ddl_main='''
#      set bail on;
#      create or alter user %(EDS_USER)s password '%(EDS_PSWD)s' using plugin Legacy_UserManager;
#      commit;
#
#      set term ^;
#      create procedure sp_do_eds ( a_target_db varchar(128) ) returns( source_dts timestamp, who_is_connecting varchar(128), source_db varchar(128), target_db varchar(128), target_dts timestamp ) as
#      begin
#          source_dts = cast('now' as timestamp);
#          for
#              execute statement
#                  ('select cast(? as varchar(128)) as connect_from_db, current_user, mon$database_name as connect_to_db, cast(''now'' as timestamp) from mon$database')
#                  ( rdb$get_context('SYSTEM', 'DB_NAME') )
#                  on external
#                      'localhost:' || a_target_db
#                  as
#                      user '%(EDS_USER)s'
#                      password '%(EDS_PSWD)s'
#              into who_is_connecting, source_db, target_db, target_dts
#         do
#             suspend;
#      end
#      ^
#      set term ;^
#      commit;
#      grant execute on procedure sp_do_eds to %(EDS_USER)s;
#      grant drop database to %(EDS_USER)s;
#      commit;
#  ''' % locals()
#
#  f_isql1=open( os.path.join(context['temp_directory'],'tmp-c6182-ddl1.sql'), 'w')
#  f_isql1.write( ddl_main )
#  flush_and_close( f_isql1 )
#
#
#  ddl_eds='''
#      set bail on;
#      set term ^;
#      -- create procedure sp_del_att returns( list_of_killed varchar(255) ) as
#      create procedure sp_del_att returns( num_of_killed smallint ) as
#      begin
#          num_of_killed = 0;
#          for
#              select mon$attachment_id as killed_att
#              from mon$attachments
#              where mon$system_flag is distinct from 1 and mon$attachment_id != current_connection
#          as cursor c
#          do
#          begin
#              -- list_of_killed = list_of_killed || c.killed_att || ',';
#              delete from mon$attachments where current of c;
#              num_of_killed = num_of_killed + 1;
#          end
#          suspend;
#      end
#      ^
#      set term ;^
#      commit;
#      grant execute on procedure sp_del_att to public;
#      commit;
#  '''
#
#
#  f_isql2=open( os.path.join(context['temp_directory'],'tmp-c6182-ddl2.sql'), 'w')
#  f_isql2.write( ddl_eds )
#  flush_and_close( f_isql2 )
#
#
#  for i in range(0, DB_CNT+1):
#      dbx = os.path.join( DB_PATH, ( ('c6182_tmp4eds.%d.fdb' % i) if i > 0 else  'c6182_tmpmain.fdb' ) )
#      cleanup( (dbx,) )
#
#      con=fdb.create_database(dsn = 'localhost:' + dbx, user = user_name, password = user_password)
#      con.close()
#      subprocess.call( [context['isql_path'], '-user', DB_USER, '-pas', DB_PSWD, 'localhost:' + dbx, '-i', (f_isql1.name if i==0 else f_isql2.name) ])
#
#
#  #-----------------------------------------
#
#  con = fdb.connect( dsn = 'localhost:' + os.path.join(DB_PATH, 'c6182_tmpmain.fdb'), user = EDS_USER, password = EDS_PSWD)
#
#  cur = con.cursor()
#  for i in range(1, DB_CNT+1):
#      dbx = os.path.join( DB_PATH, ('c6182_tmp4eds.%d.fdb' % i) )
#      cur.execute( 'select * from sp_do_eds(?)', (dbx,) )
#      for r in cur:
#          pass
#          # 2debug only: print(r)
#
#      cur.close()
#      con.commit()
#
#      time.sleep( TDELAY )
#
#  #--------------------------------------------
#  con.drop_database()
#  con.close()
#  #--------------------------------------------
#
#  for i in range(1, DB_CNT+1):
#      dbx = os.path.join( DB_PATH, ('c6182_tmp4eds.%d.fdb' % i) )
#
#      con = fdb.connect( 'localhost:' + dbx, user = user_name, password = user_password)
#      cur = con.cursor()
#      cur.callproc( 'sp_del_att' )
#      for r in cur:
#          if i == 1:
#              print( 'Number of deleted attachments for DB # %d: %d' % (i, r[0] ) )
#          else:
#              # All subseq. databases are not interested for us
#              pass
#
#      cur.close()
#      con.commit()
#
#      try:
#          con.drop_database()
#      except Exception as e:
#          ls=repr(e).split('\\n')
#          print( ls[-2] )
#      finally:
#          con.close()
#
#  #--------------------------------------------
#
#  svc = services.connect( host='localhost', user = user_name, password = user_password)
#  for i in range(1, DB_CNT+1):
#      dbx = os.path.join( DB_PATH, ('c6182_tmp4eds.%d.fdb' % i) )
#      if os.path.isfile(dbx):
#          print('UNEXPECTED presence of DB '+dbx)
#          svc.shutdown(database = dbx, shutdown_mode =  fdb.services.SHUT_FULL, shutdown_method = fdb.services.SHUT_FORCE, timeout  = 0 )
#          svc.bring_online( database = dbx )
#          os.remove(dbx)
#
#  # commented 05.01.2020:
#  #######################
#  # Unable to perform the requested Service API action:
#  # - SQLCODE: -85
#  # - The user name specified was not found in the security database
#  # -85
#  # 335544753
#  # ---xxx --- svc.remove_user( EDS_USER )
#
#  svc.close()
#
#  # Use ISQL instead of FDB Services instance to drop user which was created with Legacy_UserManager plugin
#  # and this plugin now is NOT in the head of UserManager config parameter:
#  runProgram(context['isql_path'],[ dsn, '-user', DB_USER, '-pas', DB_PSWD ], 'drop user %(EDS_USER)s using plugin Legacy_UserManager;' % locals() )
#
#  cleanup( (f_isql1, f_isql2) )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    Number of deleted attachments for DB # 1: 0
"""

ddl_eds = """
set bail on;
set term ^;
-- create procedure sp_del_att returns( list_of_killed varchar(255) ) as
create procedure sp_del_att returns( num_of_killed smallint ) as
begin
    num_of_killed = 0;
    for
        select mon$attachment_id as killed_att
        from mon$attachments
        where mon$system_flag is distinct from 1 and mon$attachment_id != current_connection
    as cursor c
    do
    begin
        -- list_of_killed = list_of_killed || c.killed_att || ',';
        delete from mon$attachments where current of c;
        num_of_killed = num_of_killed + 1;
    end
    suspend;
end
^
set term ;^
commit;
grant execute on procedure sp_del_att to public;
commit;
"""

eds_user = user_factory('db_1', name='tmp$c6182_leg', password='123', plugin='Legacy_UserManager')

TDELAY = 3

def init_main_db(act_1: Action, eds_user: User):
    ddl_script = f"""
        set bail on;
        set term ^;
        create procedure sp_do_eds ( a_target_db varchar(128) ) returns( source_dts timestamp, who_is_connecting varchar(128), source_db varchar(128), target_db varchar(128), target_dts timestamp ) as
        begin
            source_dts = cast('now' as timestamp);
            for
                execute statement
                    ('select cast(? as varchar(128)) as connect_from_db, current_user, mon$database_name as connect_to_db, cast(''now'' as timestamp) from mon$database')
                    ( rdb$get_context('SYSTEM', 'DB_NAME') )
                    on external
                        'localhost:' || a_target_db
                    as
                        user '{eds_user.name}'
                        password '{eds_user.password}'
                into who_is_connecting, source_db, target_db, target_dts
           do
               suspend;
        end
        ^
        set term ;^
        commit;
        grant execute on procedure sp_do_eds to {eds_user.name};
        grant drop database to {eds_user.name};
        commit;
        """
    act_1.isql(switches=[], input=ddl_script)


@pytest.mark.version('>=4.0')
def test_1(act_1: Action, db_1_a: Database, db_1_b: Database, db_1_c: Database,
           db_1_d: Database, eds_user: User, capsys):
    #pytest.skip("Test not IMPLEMENTED")
    init_main_db(act_1, eds_user)
    for db in [db_1_a, db_1_b, db_1_c, db_1_d]:
        act_1.reset()
        act_1.isql(switches=[db.dsn], input=ddl_eds, connect_db=False)
    #
    with act_1.db.connect(user=eds_user.name, password=eds_user.password) as con:
        with con.cursor() as c:
            for db in [db_1_a, db_1_b, db_1_c, db_1_d]:
                c.execute('select * from sp_do_eds(?)', [db.db_path]).fetchall()
            time.sleep(TDELAY)
    #
    for db in [db_1_a, db_1_b, db_1_c, db_1_d]:
        with db.connect() as con:
            c = con.cursor()
            row = c.call_procedure('sp_del_att')
            if db is db_1_a:
                print(f'Number of deleted attachments for DB # 1: {row[0]}')
    #
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
