#coding:utf-8

"""
ID:          issue-4081
ISSUE:       4081
TITLE:       WITH LOCK clause is allowed for users with read-only rights on some table, thus blocking others from updating this table
DESCRIPTION:
JIRA:        CORE-3736
"""

import pytest
from firebird.qa import *

db = db_factory()

user_1_ro = user_factory('db', name='tmp$c3736_ro', password='tmp$c3736_ro')
user_1_ud = user_factory('db', name='tmp$c3736_ud', password='tmp$c3736_ud')

test_script = """
    set wng off;

    recreate table t_read_only_for_non_sys(id int);
    commit;
    insert into t_read_only_for_non_sys values(1);
    insert into t_read_only_for_non_sys values(2);
    insert into t_read_only_for_non_sys values(3);
    insert into t_read_only_for_non_sys values(4);
    insert into t_read_only_for_non_sys values(5);
    commit;

    grant select on t_read_only_for_non_sys to tmp$c3736_ro;
    commit;
    grant update,delete,select on t_read_only_for_non_sys to tmp$c3736_ud;
    commit;

    set transaction no wait;

    update t_read_only_for_non_sys set id = id where id >= 4;

    set term ^;
    execute block returns( who_am_i type of column sec$users.sec$user_name, my_action varchar(20), what_i_see int )
    as
      declare v_dbname type of column mon$database.mon$database_name;
      declare v_usr_ro type of column sec$users.sec$user_name = 'tmp$c3736_ro';
      declare v_pwd_ro varchar(20) = 'tmp$c3736_ro';
      declare v_connect varchar(255);
    begin
      select 'localhost:' || d.mon$database_name
      from mon$database d
      into v_dbname;

      for
        execute statement 'select current_user, ''select_read_only'', id from t_read_only_for_non_sys' --  for update with lock'
        on external (v_dbname)
        as user (v_usr_ro) password (v_pwd_ro)
        into who_am_i, my_action, what_i_see
      do
        suspend;

      for
        execute statement 'select current_user, ''select_with_lock'', id from t_read_only_for_non_sys for update with lock'
        on external (v_dbname)
        as user (v_usr_ro) password (v_pwd_ro)
        into who_am_i, my_action, what_i_see
      do
        suspend;


    end
    ^
    set term ;^
    rollback;

    set transaction no wait;

    update t_read_only_for_non_sys set id = id where id >= 4;

    set term ^;
    execute block returns( who_am_i type of column sec$users.sec$user_name, my_action varchar(20), what_i_see int )
    as
      declare v_dbname type of column mon$database.mon$database_name;
      declare v_usr_ud type of column sec$users.sec$user_name = 'tmp$c3736_ud';
      declare v_pwd_ud varchar(20) = 'tmp$c3736_ud';
      declare v_connect varchar(255);
    begin
      select 'localhost:' || d.mon$database_name
      from mon$database d
      into v_dbname;

      for
        execute statement 'select current_user, ''select_with_lock'', id from t_read_only_for_non_sys for update with lock'
        on external (v_dbname)
        as user (v_usr_ud) password (v_pwd_ud)
        into who_am_i, my_action, what_i_see
      do
        suspend;

    end
    ^
    set term ;^
    rollback;

    --                                    ||||||||||||||||||||||||||||
    -- ###################################|||  FB 4.0+, SS and SC  |||##############################
    --                                    ||||||||||||||||||||||||||||
    -- If we check SS or SC and ExtConnPoolLifeTime > 0 (config parameter FB 4.0+) then current
    -- DB (bugs.core_NNNN.fdb) will be 'captured' by firebird.exe process and fbt_run utility
    -- will not able to drop this database at the final point of test.
    -- Moreover, DB file will be hold until all activity in firebird.exe completed and AFTER this
    -- we have to wait for <ExtConnPoolLifeTime> seconds after it (discussion and small test see
    -- in the letter to hvlad and dimitr 13.10.2019 11:10).
    -- This means that one need to kill all connections to prevent from exception on cleanup phase:
    -- SQLCODE: -901 / lock time-out on wait transaction / object <this_test_DB> is in use
    -- #############################################################################################
    delete from mon$attachments where mon$attachment_id != current_connection;
    commit;
"""

act = isql_act('db', test_script,
                 substitutions=[('^((?!335544352|335544878).)*$', ''), ('number is.*', '')])

expected_stdout = """
    WHO_AM_I                        MY_ACTION              WHAT_I_SEE
    =============================== ==================== ============
    TMP$C3736_RO                    select_read_only                1
    TMP$C3736_RO                    select_read_only                2
    TMP$C3736_RO                    select_read_only                3
    TMP$C3736_RO                    select_read_only                4
    TMP$C3736_RO                    select_read_only                5


    WHO_AM_I                        MY_ACTION              WHAT_I_SEE
    =============================== ==================== ============
    TMP$C3736_UD                    select_with_lock                1
    TMP$C3736_UD                    select_with_lock                2
    TMP$C3736_UD                    select_with_lock                3
"""

expected_stderr = """
    335544352 : no permission for UPDATE access to TABLE T_READ_ONLY_FOR_NON_SYS
    335544878 : concurrent transaction number is 806
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action, user_1_ro: User, user_1_ud: User):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

