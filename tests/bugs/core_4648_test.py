#coding:utf-8
#
# id:           bugs.core_4648
# title:        no permission for CREATE access to DATABASE (for RDB$ADMIN)
# decription:
# tracker_id:   CORE-4648
# min_versions: ['3.0']
# versions:     3.0
# qmid:

import pytest
from io import BytesIO
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, user_factory, User, temp_file
from firebird.driver import SrvRestoreFlag

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = ""

#init_script_1 = """
    #set wng off;
    #create or alter user tmp$c4648 password '123' revoke admin role;
    #commit;
    #revoke all on all from tmp$c4648;
    #-- 'create ... grant admin role' or 'grant rdb$admin' are NOT neccessary
    #-- for enabling to creating database by non-sysdba user:
    #grant create database to user tmp$c4648;
    #commit;
#"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#
#  print ('Starting backup...')
#  fbk = os.path.join(context['temp_directory'],'tmp4648.fbk')
#  fdn = 'localhost:'+os.path.join(context['temp_directory'],'tmp4648.tmp')
#  runProgram('gbak',['-b','-user',user_name,'-password',user_password,dsn,fbk])
#  print ('Backup finished.')
#  print ('Starting restore using NON sysdba user account...')
#  runProgram('gbak',['-rep','-user','TMP$C4648','-password','123',fbk,fdn])
#  print ('Restore using NON sysdba user account finished.')
#  if os.path.isfile(fbk):
#      print ('Delete backup file...')
#      os.remove(fbk)
#      print ('Backup file deleted.')
#
#  script = '''
#      set list on;
#      select
#           a.mon$user as "Who am I:"
#          ,left(a.mon$remote_protocol,3) as "Used protocol:"
#          ,iif(m.mon$database_name containing 'tmp4648.tmp','YES','NO! ' || m.mon$database_name ) as "Connected to restored DB ?"
#          ,m.mon$owner as "Owner of DB is:"
#      from mon$attachments a, mon$database m
#      where a.mon$attachment_id=current_connection;
#      commit;
#      drop database;
#  '''
#  print ('Starting ISQL using NON sysdba user account...')
#  runProgram('isql',[fdn,'-q','-user','tmp$c4648','-pas','123'],script)
#  print ('ISQL using NON sysdba user account finished.')
#
#  script='''revoke create database from user tmp$c4648;
#  drop user tmp$c4648;
#  commit;
#  '''
#  runProgram('isql',[dsn,'-q','-user',user_name,'-password',user_password],script)
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    Starting backup...
    Backup finished.
    Starting restore using NON sysdba user account...
    Restore using NON sysdba user account finished.
    Starting ISQL using NON sysdba user account...
    Who am I:                       TMP$C4648
    Used protocol:                  TCP
    Connected to restored DB ?      YES
    Owner of DB is:                 TMP$C4648
    ISQL using NON sysdba user account finished.
"""

user_1 = user_factory(name='tmp$c4648', password='123')
temp_db_1 = temp_file('tmp4648.fdb')

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, user_1: User, temp_db_1: Path, capsys):
    with act_1.db.connect() as con:
        c = con.cursor()
        #-- 'create ... grant admin role' or 'grant rdb$admin' are NOT neccessary
        #-- for enabling to creating database by non-sysdba user:
        c.execute('grant create database to user tmp$c4648')
        con.commit()
    #
    print ('Starting backup...')
    backup = BytesIO()
    with act_1.connect_server() as srv:
        srv.database.local_backup(database=str(act_1.db.db_path), backup_stream=backup)
        print ('Backup finished.')
    backup.seek(0)
    with act_1.connect_server(user=user_1.name, password=user_1.password) as srv:
        print ('Starting restore using NON sysdba user account...')
        srv.database.local_restore(database=str(temp_db_1), backup_stream=backup,
                                   flags=SrvRestoreFlag.REPLACE)
        print ('Restore using NON sysdba user account finished.')
    #
    script = """
    set list on;
    select
         a.mon$user as "Who am I:"
        ,left(a.mon$remote_protocol,3) as "Used protocol:"
        ,iif(m.mon$database_name containing 'tmp4648.fdb','YES','NO! ' || m.mon$database_name ) as "Connected to restored DB ?"
        ,m.mon$owner as "Owner of DB is:"
    from mon$attachments a, mon$database m
    where a.mon$attachment_id=current_connection;
    commit;
    """
    print ('Starting ISQL using NON sysdba user account...')
    act_1.isql(switches=['-q', '-user', 'tmp$c4648', '-pas', '123', f'localhost:{temp_db_1}'],
               connect_db=False, input=script)
    print(act_1.stdout)
    print ('ISQL using NON sysdba user account finished.')
    act_1.reset()
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
