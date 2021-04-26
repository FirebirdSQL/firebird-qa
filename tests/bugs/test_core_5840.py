#coding:utf-8
#
# id:           bugs.core_5840
# title:        Ignor of reference privilege
# decription:   
#                  Checked on:
#                       4.0.0.1000 SS
#                       3.0.4.32985 SS
#                
# tracker_id:   CORE-5840
# min_versions: ['3.0.4']
# versions:     3.0.4, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set wng off;

    create or alter user tmp$c5840 password '123';
    revoke all on all from tmp$c5840;
    grant create table to tmp$c5840;
    commit;

    create table test1(
        id int not null primary key using index test1_pk, 
        pid int
    );
    commit;

    create table test3(id int primary key, pid int, constraint test3_fk foreign key(pid) references test1(id) using index test3_fk);
    commit;

    connect '$(DSN)' user 'tmp$c5840' password '123';

    -- this should FAIL, table must not be created at all:
    create table test2(
        id int primary key, 
        pid int, 
        constraint test2_fk foreign key(pid) references test1(id) using index test2_fk
    );
    commit;

    --set echo on;
    alter table test3 drop constraint test3_fk; -- this WAS allowed (error!)
    commit;

    alter table test1 add constraint test1_fk foreign key(pid) references test1(id) using index test1_fk;
    commit;

    alter table test1 drop constraint test1_fk; -- this was prohibited BEFORE this ticket; we only check this again here
    commit;

    set echo off;

    set list on;
    select rdb$relation_name from rdb$relations where rdb$system_flag is distinct from 1;
    commit;

    -- cleanup:
    connect '$(DSN)' user 'SYSDBA' password 'masterkey'; -- mandatory!
    drop user tmp$c5840;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$RELATION_NAME               TEST1
    RDB$RELATION_NAME               TEST3
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -CREATE TABLE TEST2 failed
    -no permission for REFERENCES access to TABLE TEST1

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER TABLE TEST3 failed
    -no permission for ALTER access to TABLE TEST3

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER TABLE TEST1 failed
    -no permission for ALTER access to TABLE TEST1

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER TABLE TEST1 failed
    -no permission for ALTER access to TABLE TEST1
  """

@pytest.mark.version('>=3.0.4,<4.0')
def test_core_5840_1(act_1: Action):
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
    set wng off;

    create or alter user tmp$c5840 password '123';
    revoke all on all from tmp$c5840;
    grant create table to tmp$c5840;
    commit;

    create table test1(
        id int not null primary key using index test1_pk, 
        pid int
    );
    commit;

    create table test3(id int primary key, pid int, constraint test3_fk foreign key(pid) references test1(id) using index test3_fk);
    commit;

    connect '$(DSN)' user 'tmp$c5840' password '123';

    -- this should FAIL, table must not be created at all:
    create table test2(
        id int primary key, 
        pid int, 
        constraint test2_fk foreign key(pid) references test1(id) using index test2_fk
    );
    commit;

    --set echo on;
    alter table test3 drop constraint test3_fk; -- this WAS allowed (error!)
    commit;

    alter table test1 add constraint test1_fk foreign key(pid) references test1(id) using index test1_fk;
    commit;

    alter table test1 drop constraint test1_fk; -- this was prohibited BEFORE this ticket; we only check this again here
    commit;

    set echo off;

    set list on;
    select rdb$relation_name from rdb$relations where rdb$system_flag is distinct from 1;
    commit;

    -- cleanup:
    connect '$(DSN)' user 'SYSDBA' password 'masterkey'; -- mandatory!
    drop user tmp$c5840;
    commit;
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    RDB$RELATION_NAME               TEST1
    RDB$RELATION_NAME               TEST3
  """
expected_stderr_2 = """
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -CREATE TABLE TEST2 failed
    -no permission for REFERENCES access to TABLE TEST1
    -Effective user is TMP$C5840

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER TABLE TEST3 failed
    -no permission for ALTER access to TABLE TEST3
    -Effective user is TMP$C5840

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER TABLE TEST1 failed
    -no permission for ALTER access to TABLE TEST1
    -Effective user is TMP$C5840

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER TABLE TEST1 failed
    -no permission for ALTER access to TABLE TEST1
    -Effective user is TMP$C5840
  """

@pytest.mark.version('>=4.0')
def test_core_5840_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_expected_stderr == act_2.clean_stderr
    assert act_2.clean_expected_stdout == act_2.clean_stdout

