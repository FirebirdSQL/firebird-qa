#coding:utf-8
#
# id:           bugs.core_5082
# title:        Server does not validate correctness of user/password pair provided in EXECUTE STATEMENT operator
# decription:   
#                   Confirmed on build 32136 (RC1), build 32181: wrongly displayed names of non-existent user 'TMP$C5082'
#                   and user SYDSDBA that login was provided with wrong (but NOT empty) password.
#                   NOTE: check does NOT perform inside ES when password is empty string or any number of ascii_char(32) 
#                   and 'new' user specified is equal to user name that was used to login - see examples here when password
#                   for SYSDBA is '' or ascii_char(32).
#               
#                   06.02.2019: added separate code for 4.0 because of new error message ("Missing security context for ...")
#                   Checked on: 4.0.0.1421 SS, CS.
#               
#               
#                   30.12.2019: removed check for all detailed messages about error except SQLSTATE:
#                   it is enough to check that server does not allow to perform such logins.
#                   Checked on:
#                       4.0.0.1712 SS: 1.134s.
#                       4.0.0.1346 SC: 1.563s.
#                       4.0.0.1691 CS: 1.878s.
#                       3.0.5.33218 SS: 0.637s.
#                       3.0.5.33084 SC: 1.058s.
#                       3.0.5.33212 CS: 1.613s.
#               
#                 
# tracker_id:   CORE-5082
# min_versions: ['3.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('-At block line: [\\d]+, col: [\\d]+', '-At block line')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Make sure that user 'TMP$C5082' does NOT exist at the point just before this test start:
    create or alter user tmp$c5082 password '123';
    commit;
    drop user tmp$c5082;
    commit;

    set list on;
    set term ^;
    execute block returns (whoami varchar(32)) as 
    begin 
        execute statement 'select current_user from rdb$database' as user 'TMP$C5082' password 'qwecXzasd' into whoami; 
        suspend; 
    end
    ^

    execute block returns (whoami varchar(32)) as 
    begin 
        execute statement 'select current_user from rdb$database' as user 'TMP$C5082' password '' into whoami; 
        suspend; 
    end
    ^
    
    execute block returns (whoami varchar(32)) as 
    begin 
        execute statement 'select current_user from rdb$database' as user 'SYSDBA' password 'fullyWrong' into whoami; 
        suspend; 
    end
    ^ 

    execute block returns (whoami varchar(32)) as 
    begin 
        execute statement 'select current_user from rdb$database' as user 'SYSDBA' password '' into whoami; 
        suspend; 
    end
    ^ 

    execute block returns (whoami varchar(32)) as 
    begin 
        execute statement 'select current_user from rdb$database' as user 'SYSDBA' password ' ' into whoami; 
        suspend; 
    end
    ^ 

    execute block returns (whoami varchar(32)) as 
    begin 
        execute statement 'select current_user from rdb$database' as user 'SYSDBA' password '	' into whoami; 
        --                                                                                   ^- Tab character here!
        suspend; 
    end
    ^ 

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WHOAMI                          SYSDBA
    WHOAMI                          SYSDBA
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    Your user name and password are not defined. Ask your database administrator to set up a Firebird login.
    -At block line: 3, col: 9

    Statement failed, SQLSTATE = 28000
    Your user name and password are not defined. Ask your database administrator to set up a Firebird login.
    -At block line: 3, col: 9

    Statement failed, SQLSTATE = 28000
    Your user name and password are not defined. Ask your database administrator to set up a Firebird login.
    -At block line: 3, col: 9

    Statement failed, SQLSTATE = 28000
    Your user name and password are not defined. Ask your database administrator to set up a Firebird login.
    -At block line: 3, col: 9
  """

@pytest.mark.version('>=3.0,<4.0')
def test_core_5082_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = [('-At block line: [\\d]+, col: [\\d]+', ''), ('Missing security context.*', ''), ('Your user name and password are not defined.*', '')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    -- Make sure that user 'TMP$C5082' does NOT exist at the point just before this test start:
    create or alter user tmp$c5082 password '123';
    commit;
    drop user tmp$c5082;
    commit;

    set list on;
    set term ^;
    execute block returns (whoami varchar(32)) as 
    begin 
        execute statement 'select current_user from rdb$database' as user 'TMP$C5082' password 'qwecXzasd' into whoami; 
        suspend; 
    end
    ^

    execute block returns (whoami varchar(32)) as 
    begin 
        execute statement 'select current_user from rdb$database' as user 'TMP$C5082' password '' into whoami; 
        suspend; 
    end
    ^
    
    execute block returns (whoami varchar(32)) as 
    begin 
        execute statement 'select current_user from rdb$database' as user 'SYSDBA' password 'fullyWrong' into whoami; 
        suspend; 
    end
    ^ 

    execute block returns (whoami varchar(32)) as 
    begin 
        execute statement 'select current_user from rdb$database' as user 'SYSDBA' password '' into whoami; 
        suspend; 
    end
    ^ 

    execute block returns (whoami varchar(32)) as 
    begin 
        execute statement 'select current_user from rdb$database' as user 'SYSDBA' password ' ' into whoami; 
        suspend; 
    end
    ^ 

    execute block returns (whoami varchar(32)) as 
    begin 
        execute statement 'select current_user from rdb$database' as user 'SYSDBA' password '	' into whoami; 
        --                                                                                   ^- Tab character here!
        suspend; 
    end
    ^ 

  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    WHOAMI                          SYSDBA
    WHOAMI                          SYSDBA
  """
expected_stderr_2 = """
    Statement failed, SQLSTATE = 28000

    Statement failed, SQLSTATE = 28000

    Statement failed, SQLSTATE = 28000

    Statement failed, SQLSTATE = 28000
  """

@pytest.mark.version('>=4.0')
def test_core_5082_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_expected_stderr == act_2.clean_stderr
    assert act_2.clean_expected_stdout == act_2.clean_stdout

