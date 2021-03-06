#coding:utf-8
#
# id:           bugs.core_2724
# title:        Validate or transform string of DML queries so that engine internals doesn't receive malformed strings
# decription:   
#                  Code from doc/sql.extensions/README.ddl_triggers.txt was taken as basis for this test
#                  (see ticket issue: "This situation happened with DDL triggers ...").
#                  Several DB objects are created here and their DDL contain unicode (Greek) text.
#                  Attachment these issues these DDL intentionally is run with charset = NONE. 
#                  This charset (NONE) should result in question marks after we finish DDL and want to query log table
#                  that was filled by DDL trigger and contains issued DDL statements.
#                
# tracker_id:   CORE-2724
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('SQL_TEXT .*', 'SQL_TEXT'), ('RESULT_INFO .*', 'RESULT_INFO')]

init_script_1 = """
    create sequence ddl_seq;

    create table ddl_log (
        id bigint not null primary key,
        moment timestamp not null,
        current_connection_cset varchar(31) not null,
        event_type varchar(25) not null,
        object_type varchar(25) not null,
        ddl_event varchar(25) not null,
        object_name varchar(31) not null,
        old_object_name varchar(31),
        new_object_name varchar(31),
        sql_text blob sub_type text not null,
        ok char(1) not null,
        result_info blob sub_type text
    );
    commit;
    
    set term ^;
    create trigger trig_ddl_log_before before any ddl statement
    as
        declare id type of column ddl_log.id;
        declare v_current_connection_cset varchar(31);
    begin
        -- We do the changes in an AUTONOMOUS TRANSACTION, so if an exception happens and the command
        -- didn't run, the log will survive.
        in autonomous transaction do
        begin
            
            select coalesce(c.rdb$character_set_name, '??? NULL ???')
            from mon$attachments a
            left join rdb$character_sets c on a.mon$character_set_id = c.rdb$character_set_id
            where a.mon$attachment_id = current_connection
            into v_current_connection_cset;
        
            insert into ddl_log (id, moment, current_connection_cset, 
                                 event_type, object_type, ddl_event, object_name,
                                 old_object_name, new_object_name, sql_text, ok, result_info)
                values (next value for ddl_seq, 
                        'now', 
                        :v_current_connection_cset,
                        rdb$get_context('DDL_TRIGGER', 'EVENT_TYPE'),
                        rdb$get_context('DDL_TRIGGER', 'OBJECT_TYPE'),
                        rdb$get_context('DDL_TRIGGER', 'DDL_EVENT'),
                        rdb$get_context('DDL_TRIGGER', 'OBJECT_NAME'),
                        rdb$get_context('DDL_TRIGGER', 'OLD_OBJECT_NAME'),
                        rdb$get_context('DDL_TRIGGER', 'NEW_OBJECT_NAME'),
                        rdb$get_context('DDL_TRIGGER', 'SQL_TEXT'),
                        'N',
                        'Κάτι συνέβη. Θα πρέπει να ελέγξετε') -- Something was wrong. One need to check this.
                returning id into id;
            rdb$set_context('USER_SESSION', 'trig_ddl_log_id', id);
        end
    end
    ^
    
    -- Note: the above trigger will fire for this DDL command. It's good idea to use -nodbtriggers
    -- when working with them!
    create trigger trig_ddl_log_after after any ddl statement
    as
    begin
        -- Here we need an AUTONOMOUS TRANSACTION because the original transaction will not see the
        -- record inserted on the BEFORE trigger autonomous transaction if user transaction is not
        -- READ COMMITTED.
        in autonomous transaction do
            update ddl_log set ok = 'Y', 
            result_info = 'Τα πάντα ήταν επιτυχής' -- Everything has completed successfully
            where id = rdb$get_context('USER_SESSION', 'trig_ddl_log_id');
    end
    ^
    set term ;^
    commit;
    
    -- So lets delete the record about trig_ddl_log_after creation.
    delete from ddl_log;
    commit;
  """

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import time
#  import subprocess
#  
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
#  sql_check='''    delete from ddl_log;
#      commit;
#  
#      create domain dm_name varchar(50) check (value in ('αμορτισέρ', 'κόμβο', 'σωλήνα', 'φέροντα', 'βραχίονα'));
#      recreate table t1 (
#           saller_id integer  -- αναγνωριστικό εμπόρου // ID of saler
#          ,customer_id integer  -- αναγνωριστικό πελάτη // ID of customer
#          ,product_name dm_name
#      );
#      commit;
#      set list on;
#      
#      select id, current_connection_cset, sql_text, result_info, ddl_event, object_name
#      from ddl_log order by id;
#      
#      commit;
#      drop table t1;
#      drop domain dm_name;
#      exit;
#  '''
#  
#  f_check_sql = open( os.path.join(context['temp_directory'],'tmp_check_2724.sql'), 'w')
#  f_check_sql.write(sql_check)
#  flush_and_close( f_check_sql )
#  
#  ##########################################################################################
#  
#  f_ch_none_log = open( os.path.join(context['temp_directory'],'tmp_ch_none_2724.log'), 'w')
#  f_ch_none_err = open( os.path.join(context['temp_directory'],'tmp_ch_none_2724.err'), 'w')
#  
#  subprocess.call( [context['isql_path'], dsn, "-i", f_check_sql.name,
#                   "-ch", "none"],
#                   stdout = f_ch_none_log,
#                   stderr = f_ch_none_err
#                 )
#  
#  flush_and_close( f_ch_none_log )
#  flush_and_close( f_ch_none_err )
#  
#  ##########################################################################################
#  
#  f_ch_utf8_log = open( os.path.join(context['temp_directory'],'tmp_ch_utf8_2724.log'), 'w')
#  f_ch_utf8_err = open( os.path.join(context['temp_directory'],'tmp_ch_utf8_2724.err'), 'w')
#  
#  subprocess.call( [context['isql_path'], dsn, "-user", user_name, "-password", user_password, "-i", f_check_sql.name,
#                    "-ch", "utf8"],
#                   stdout = f_ch_utf8_log,
#                   stderr = f_ch_utf8_err
#                 )
#  flush_and_close( f_ch_utf8_log )
#  flush_and_close( f_ch_utf8_err )
#  
#  
#  f_list = [f_ch_none_log, f_ch_none_err, f_ch_utf8_log, f_ch_utf8_err]
#  for f in f_list:
#      with open( f.name,'r') as f:
#         print(f.read())
#  
#  
#  # Cleanup
#  #########
#  time.sleep(1)
#  
#  f_list.append(f_check_sql)
#  cleanup( [i.name for i in f_list] )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              2
    CURRENT_CONNECTION_CSET         NONE                           
    SQL_TEXT                        
    create domain dm_name varchar(50) check (value in ('??????????????????', '??????????', '????????????', '??????????????', '????????????????'))
    RESULT_INFO                     
    Τα πάντα ήταν επιτυχής
    DDL_EVENT                       CREATE DOMAIN
    OBJECT_NAME                     DM_NAME

    ID                              3
    CURRENT_CONNECTION_CSET         NONE                           
    SQL_TEXT                        
    recreate table t1 (
             saller_id integer  -- ?????????????????????????? ?????????????? // ID of saler
            ,customer_id integer  -- ?????????????????????????? ???????????? // ID of customer
            ,product_name dm_name
        )
    RESULT_INFO                     
    Τα πάντα ήταν επιτυχής
    DDL_EVENT                       CREATE TABLE
    OBJECT_NAME                     T1  
    
    ID                              6
    CURRENT_CONNECTION_CSET         UTF8                           
    SQL_TEXT                        80:0
    create domain dm_name varchar(50) check (value in ('αμορτισέρ', 'κόμβο', 'σωλήνα', 'φέροντα', 'βραχίονα'))
    RESULT_INFO                     80:2
    Τα πάντα ήταν επιτυχής
    DDL_EVENT                       CREATE DOMAIN
    OBJECT_NAME                     DM_NAME

    ID                              7
    CURRENT_CONNECTION_CSET         UTF8                           
    SQL_TEXT                        
    recreate table t1 (
             saller_id integer  -- αναγνωριστικό εμπόρου // ID of saler
            ,customer_id integer  -- αναγνωριστικό πελάτη // ID of customer
            ,product_name dm_name
        )
    RESULT_INFO                     
    Τα πάντα ήταν επιτυχής
    DDL_EVENT                       CREATE TABLE
    OBJECT_NAME                     T1    
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


