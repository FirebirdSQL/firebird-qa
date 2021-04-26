#coding:utf-8
#
# id:           bugs.core_4342
# title:        Non-privileged user can delete records from RDB$SECURITY_CLASSES table
# decription:   
# tracker_id:   CORE-4342
# min_versions: ['3.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter user boss password '123';
    create or alter user mngr password '456';
    commit;

    -- Add these DDL privileges in order to have some rows in 
    -- rdb$security_classes table for user BOSS:
    grant create table to boss;
    grant alter any table to boss;
    grant drop any table to boss;
    commit;

    set list on;
    select current_user,count(*) acl_count from rdb$security_classes where rdb$acl containing 'boss';

    select 1 from rdb$security_classes where rdb$acl containing 'boss' with lock;
    update rdb$security_classes set rdb$security_class = rdb$security_class where rdb$acl containing 'boss';
    delete from rdb$security_classes where rdb$acl containing 'boss'; 
    commit;

    connect '$(DSN)' user 'MNGR' password '456';
    select current_user,count(*) acl_count from rdb$security_classes where rdb$acl containing 'boss';

    select 1 from rdb$security_classes where rdb$acl containing 'boss' with lock;
    update rdb$security_classes set rdb$security_class = rdb$security_class where rdb$acl containing 'boss';
    delete from rdb$security_classes where rdb$acl containing 'boss'; 
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    drop user mngr;
    drop user boss;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    USER                            SYSDBA
    ACL_COUNT                       1

    USER                            MNGR
    ACL_COUNT                       1
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = HY000
    Cannot select system table RDB$SECURITY_CLASSES for update WITH LOCK

    Statement failed, SQLSTATE = 42000
    UPDATE operation is not allowed for system table RDB$SECURITY_CLASSES

    Statement failed, SQLSTATE = 42000
    DELETE operation is not allowed for system table RDB$SECURITY_CLASSES

    Statement failed, SQLSTATE = HY000
    Cannot select system table RDB$SECURITY_CLASSES for update WITH LOCK

    Statement failed, SQLSTATE = 28000
    no permission for UPDATE access to TABLE RDB$SECURITY_CLASSES

    Statement failed, SQLSTATE = 28000
    no permission for DELETE access to TABLE RDB$SECURITY_CLASSES
  """

@pytest.mark.version('>=3.0,<4.0')
def test_core_4342_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    create or alter user boss password '123';
    create or alter user mngr password '456';
    commit;

    -- Add these DDL privileges in order to have some rows in 
    -- rdb$security_classes table for user BOSS:
    grant create table to boss;
    grant alter any table to boss;
    grant drop any table to boss;
    commit;

    set list on;
    select current_user,count(*) acl_count from rdb$security_classes where rdb$acl containing 'boss';

    select 1 from rdb$security_classes where rdb$acl containing 'boss' with lock;
    update rdb$security_classes set rdb$security_class = rdb$security_class where rdb$acl containing 'boss';
    delete from rdb$security_classes where rdb$acl containing 'boss'; 
    commit;

    connect '$(DSN)' user 'MNGR' password '456';
    select current_user,count(*) acl_count from rdb$security_classes where rdb$acl containing 'boss';

    select 1 from rdb$security_classes where rdb$acl containing 'boss' with lock;
    update rdb$security_classes set rdb$security_class = rdb$security_class where rdb$acl containing 'boss';
    delete from rdb$security_classes where rdb$acl containing 'boss'; 
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    drop user mngr;
    drop user boss;
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    USER                            SYSDBA
    ACL_COUNT                       1

    USER                            MNGR
    ACL_COUNT                       1
  """
expected_stderr_2 = """
    Statement failed, SQLSTATE = HY000
    Cannot select system table RDB$SECURITY_CLASSES for update WITH LOCK
    Statement failed, SQLSTATE = 42000
    UPDATE operation is not allowed for system table RDB$SECURITY_CLASSES
    Statement failed, SQLSTATE = 42000
    DELETE operation is not allowed for system table RDB$SECURITY_CLASSES
    Statement failed, SQLSTATE = HY000
    Cannot select system table RDB$SECURITY_CLASSES for update WITH LOCK
    Statement failed, SQLSTATE = 28000
    no permission for UPDATE access to TABLE RDB$SECURITY_CLASSES
    -Effective user is MNGR
    Statement failed, SQLSTATE = 28000
    no permission for DELETE access to TABLE RDB$SECURITY_CLASSES
    -Effective user is MNGR
  """

@pytest.mark.version('>=4.0')
def test_core_4342_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_expected_stderr == act_2.clean_stderr
    assert act_2.clean_expected_stdout == act_2.clean_stdout

