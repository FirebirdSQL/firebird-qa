#coding:utf-8

"""
ID:          syspriv.access-any-object
TITLE:       Check ability to query, modify and deleting data plus add/drop constraints on any table
DESCRIPTION:
  We create two master-detail tables (under SYSDBA) and add some data to them.
  Then we connect as U01 who has system privilege to query and change (including deletion) data from ANY table.
  Under this user we first try to run DML statements (IUD) and after - to remove some old and create new
  constraint.
FBTEST:      functional.syspriv.access_any_object
"""

import pytest
from firebird.qa import *

db = db_factory()
test_user = user_factory('db', name='u01', do_not_create=True)

test_script = """
    set wng off;
    set bail on;
    set list on;

    create or alter view v_check as
    select
         current_user as who_ami
        ,r.rdb$role_name
        ,rdb$role_in_use(r.rdb$role_name) as RDB_ROLE_IN_USE
        ,r.rdb$system_privileges
    from mon$database m cross join rdb$roles r;
    commit;
    grant select on v_check to public;

    recreate table tdetl(
        id int,
        pid int,
        x int,
        y int,
        constraint tdetl_pk primary key(id),
        constraint tdetl_x_unq unique(x),
        constraint tdetl_y_gz check(y>0)
    );
    recreate table tmain(id int, constraint tmain_pk primary key(id));
    commit;

    insert into tmain(id) values(1);
    insert into tdetl(id, pid, x, y) values(10, 1, 111, 7);
    insert into tdetl(id, pid, x, y) values(20, 1, 222, 6);
    insert into tdetl(id, pid, x, y) values(30, 1, 333, 5);
    commit;

    create or alter user u01 password '123' revoke admin role;
    revoke all on all from u01;
    commit;

    set term ^;
    execute block as
    begin
      execute statement 'drop role role_for_ddl_dml_any_obj';
      when any do begin end
    end^
    set term ;^
    commit;

    -- Add/change/delete non-system records in RDB$TYPES
    create role role_for_ddl_dml_any_obj
        set system privileges to
            SELECT_ANY_OBJECT_IN_DATABASE,
            MODIFY_ANY_OBJECT_IN_DATABASE,
            ACCESS_ANY_OBJECT_IN_DATABASE;
    commit;
    grant default role_for_ddl_dml_any_obj to user u01;
    commit;

    connect '$(DSN)' user u01 password '123';

    select * from v_check;
    commit;

    set count on;
    select * from tdetl;
    update tdetl set id=-id order by id desc rows 1;
    delete from tdetl order by id rows 1;
    commit;

    alter table tdetl
        add constraint tdetl_fk foreign key(pid) references tmain using index tdetl_fk_pid
        ,drop constraint tdetl_x_unq
        ,drop constraint tdetl_y_gz
        ,drop constraint tdetl_pk
    ;
    commit;

    set bail off;
    insert into tdetl(id, pid, x, y) values(40, 2, null, null); -- should issue FK violation
    insert into tdetl(id, pid, x, y) values(40, 1, 111, null); -- should NOT issue error
    insert into tdetl(id, pid, x, y) values(40, 1, 222, -777); -- should NOT issue error
    commit;

    --connect '$(DSN)' user sysdba password 'masterkey';
    --drop user u01;
    --commit;
"""

substitutions = [('[ \t]+', ' '), ('violation of FOREIGN KEY constraint .*', 'violation of FOREIGN KEY constraint')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    WHO_AMI                         U01
    RDB$ROLE_NAME                   RDB$ADMIN
    RDB_ROLE_IN_USE                 <false>
    RDB$SYSTEM_PRIVILEGES           FFFFFFFFFFFFFFFF
    WHO_AMI                         U01
    RDB$ROLE_NAME                   ROLE_FOR_DDL_DML_ANY_OBJ
    RDB_ROLE_IN_USE                 <true>
    RDB$SYSTEM_PRIVILEGES           0000070000000000
    ID                              10
    PID                             1
    X                               111
    Y                               7
    ID                              20
    PID                             1
    X                               222
    Y                               6
    ID                              30
    PID                             1
    X                               333
    Y                               5
    Records affected: 3
    Records affected: 1
    Records affected: 1
    Records affected: 0
    Records affected: 1
    Records affected: 1
"""

expected_stderr = """
    Statement failed, SQLSTATE = 23000
    violation of FOREIGN KEY constraint "TDETL_FK" on table "TDETL"
    -Foreign key reference target does not exist
    -Problematic key value is ("PID" = 2)
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action, test_user):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
