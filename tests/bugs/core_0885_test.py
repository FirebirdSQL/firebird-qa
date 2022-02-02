#coding:utf-8

"""
ID:          issue-1278
ISSUE:       1278
TITLE:       It is impossible to take away rights on update of a column
DESCRIPTION:
JIRA:        CORE-885
FBTEST:      bugs.core_0885
"""

import pytest
from firebird.qa import *

db = db_factory()
user_1_senior = user_factory('db', name='john_senior', password='sen')
user_1_junior = user_factory('db', name='mick_junior', password='jun')
role_1 = role_factory('db', name='modifier', do_not_create=True)

test_script = """
    set wng off;
    set list on;

    recreate table test(id int, text varchar(30), changed_by_user varchar(31), changed_by_role varchar(31));
    commit;

    set term ^;
    create trigger test_biu for test active before insert or update position 0 as
    begin
        new.changed_by_user = current_user;
        new.changed_by_role = current_role;
    end
    ^
    set term ;^
    commit;

    insert into test(id, text) values(1, 'Initial data, added by SYSDBA');
    insert into test(id, text) values(2, 'Initial data, added by SYSDBA');
    insert into test(id, text) values(3, 'Initial data, added by SYSDBA');
    select * from test;
    commit;

    grant select on test to public;
    grant create role to john_senior;
    grant update(text) on test to john_senior with grant option;
    commit;

    ----------------------------------------

    --set echo on;
    --show grants;
    connect '$(DSN)' user 'JOHN_SENIOR' password 'sen';
    create role modifier;
    commit;
    grant update (text) on test to modifier; -- this CAN be done by john_senior because he was granted to control access on this field
    grant modifier to mick_junior; -- this CAN be done by john_senior because he CREATED role 'modifier' and thus he is MEMBER of it.
    commit;
    --show grants;

    connect '$(DSN)' user 'MICK_JUNIOR' password 'jun' role 'MODIFIER';
    select current_user, current_role from rdb$database;
    update test set text = 'Update-1: through the ROLE' where id = 1;
    select * from test;

    commit;

    connect '$(DSN)' user 'JOHN_SENIOR' password 'sen';
    select current_user, current_role from rdb$database;
    update test set text = 'Update-2: directly by USER' where id = 2;
    select * from test;
    commit;

    connect '$(DSN)' user 'JOHN_SENIOR' password 'sen';

    -- ###########################################################################################
    -- ###   H e r e    w e    R E V O K E    r i g h t   t o    u p d a t e     c o l u m n   ###
    -- ###########################################################################################
    -- ::: NB ::: See CORE-4836:
    -- As of WI-T3.0.0.31873, if we want to revoke privilege on certain COLUMN update, we must do
    -- it immediatelly after reconnect, NO issuing any DML here (like `select * from test` etc).

    revoke update(text) on test from modifier; -------------  ###########   R E V O K E   ########
    commit;

    connect '$(DSN)' user 'MICK_JUNIOR' password 'jun' role 'MODIFIER';
    select current_user, current_role from rdb$database;
    update test set text = 'Update-3: again using ROLE' where id = 3;
    select * from test;

    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';

    --drop role modifier;
    drop table test;
    commit;
"""

act = isql_act('db', test_script, substitutions=[('-Effective user is.*', '')])

expected_stdout = """
    ID                              1
    TEXT                            Initial data, added by SYSDBA
    CHANGED_BY_USER                 SYSDBA
    CHANGED_BY_ROLE                 NONE
    ID                              2
    TEXT                            Initial data, added by SYSDBA
    CHANGED_BY_USER                 SYSDBA
    CHANGED_BY_ROLE                 NONE
    ID                              3
    TEXT                            Initial data, added by SYSDBA
    CHANGED_BY_USER                 SYSDBA
    CHANGED_BY_ROLE                 NONE


    USER                            MICK_JUNIOR
    ROLE                            MODIFIER
    ID                              1
    TEXT                            Update-1: through the ROLE
    CHANGED_BY_USER                 MICK_JUNIOR
    CHANGED_BY_ROLE                 MODIFIER
    ID                              2
    TEXT                            Initial data, added by SYSDBA
    CHANGED_BY_USER                 SYSDBA
    CHANGED_BY_ROLE                 NONE
    ID                              3
    TEXT                            Initial data, added by SYSDBA
    CHANGED_BY_USER                 SYSDBA
    CHANGED_BY_ROLE                 NONE

    USER                            JOHN_SENIOR
    ROLE                            NONE
    ID                              1
    TEXT                            Update-1: through the ROLE
    CHANGED_BY_USER                 MICK_JUNIOR
    CHANGED_BY_ROLE                 MODIFIER
    ID                              2
    TEXT                            Update-2: directly by USER
    CHANGED_BY_USER                 JOHN_SENIOR
    CHANGED_BY_ROLE                 NONE
    ID                              3
    TEXT                            Initial data, added by SYSDBA
    CHANGED_BY_USER                 SYSDBA
    CHANGED_BY_ROLE                 NONE

    USER                            MICK_JUNIOR
    ROLE                            MODIFIER
    ID                              1
    TEXT                            Update-1: through the ROLE
    CHANGED_BY_USER                 MICK_JUNIOR
    CHANGED_BY_ROLE                 MODIFIER
    ID                              2
    TEXT                            Update-2: directly by USER
    CHANGED_BY_USER                 JOHN_SENIOR
    CHANGED_BY_ROLE                 NONE
    ID                              3
    TEXT                            Initial data, added by SYSDBA
    CHANGED_BY_USER                 SYSDBA
    CHANGED_BY_ROLE                 NONE
"""

expected_stderr = """
    Statement failed, SQLSTATE = 28000
    no permission for UPDATE access to TABLE TEST
"""


@pytest.mark.version('>=3.0')
def test_1(act: Action, user_1_senior: User, user_1_junior: User, role_1: Role):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

