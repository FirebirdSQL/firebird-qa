#coding:utf-8
#
# id:           bugs.core_5770
# title:        User who is allowed to manage other users must have this ability WITHOUT need to grant him RDB$ADMIN role
# decription:   
#                   ::::: NB ::::
#                   Could not check actual result of fbtest execution, done only using ISQL and copy its result here.
#                   Checked on WI-T4.0.0.927, Win 64x.
#                   Checked 06.08.2018 on 4.0.0.1143: OK, 4.328s.
#                 
# tracker_id:   CORE-5770
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('Use CONNECT or CREATE DATABASE.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set wng off;
    
    recreate view v_sec as
    select 
        current_user as who_am_i
        ,s.sec$user_name
        ,s.sec$active
        ,s.sec$admin
        ,s.sec$plugin
    from sec$users s 
    where upper(sec$user_name) = upper('tmp$c5770_bar');
    commit;
    grant select on v_sec to public;
    commit;

    create or alter user tmp$c5770_foo password '123' using plugin Srp grant admin role;
    create or alter user tmp$c5770_bar password '456' inactive using plugin Srp;
    commit;
    revoke all on all from tmp$c5770_foo;
    revoke all on all from tmp$c5770_bar;
    commit;

    connect '$(DSN)' user tmp$c5770_foo password '123';
    --select current_user as who_am_i from rdb$database;
    commit;
     
    -- check that sub-admin user 'foo' can make common user 'bar' ACTIVE:
    alter user tmp$c5770_bar active using plugin Srp;
    commit;
    select * from v_sec;
    commit;

    connect '$(DSN)' user tmp$c5770_bar password '456'; -- should PASS because he is ACTIVE now
    select current_user as who_am_i from rdb$database;
    commit;

    connect '$(DSN)' user tmp$c5770_foo password '123';

    -- check that sub-admin user 'foo' can make common user 'bar' INACTIVE:
    alter user tmp$c5770_bar inactive using plugin Srp;
    commit; 
    select * from v_sec;
    commit;

    -- this should raise SQLSTATE = 28000: user 'tmp$c5770_bar' again become inactive:
    connect '$(DSN)' user tmp$c5770_bar password '456';
    select current_user as who_am_i from rdb$database;
    commit;

    -- cleanup: drop foo and bar.
    connect '$(DSN)' user sysdba password 'masterkey';
    drop user tmp$c5770_foo using plugin Srp;
    drop user tmp$c5770_bar using plugin Srp;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WHO_AM_I                        TMP$C5770_FOO
    SEC$USER_NAME                   TMP$C5770_BAR
    SEC$ACTIVE                      <true>
    SEC$ADMIN                       <false>
    SEC$PLUGIN                      Srp

    WHO_AM_I                        TMP$C5770_BAR

    WHO_AM_I                        TMP$C5770_FOO
    SEC$USER_NAME                   TMP$C5770_BAR
    SEC$ACTIVE                      <false>
    SEC$ADMIN                       <false>
    SEC$PLUGIN                      Srp
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    Your user name and password are not defined. Ask your database administrator to set up a Firebird login.
  """

@pytest.mark.version('>=4.0')
def test_core_5770_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

