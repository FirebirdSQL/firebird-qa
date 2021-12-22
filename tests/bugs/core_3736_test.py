#coding:utf-8
#
# id:           bugs.core_3736
# title:        WITH LOCK clause is allowed for users with read-only rights on some table, thus blocking others from updating this table
# decription:
#                   Checked on:
#                       4.0.0.1635 SS: 1.500s.
#                       4.0.0.1633 CS: 2.032s.
#                       3.0.5.33180 SS: 1.078s.
#                       3.0.5.33178 CS: 1.408s.
#
# tracker_id:   CORE-3736
# min_versions: []
# versions:     3.0
# qmid:

import pytest
from firebird.qa import db_factory, isql_act, Action, user_factory, User

# version: 3.0
# resources: None

substitutions_1 = [('^((?!335544352|335544878).)*$', ''), ('number is.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
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

expected_stderr_1 = """
    335544352 : no permission for UPDATE access to TABLE T_READ_ONLY_FOR_NON_SYS
    335544878 : concurrent transaction number is 806
"""

user_1_ro = user_factory('db_1', name='tmp$c3736_ro', password='tmp$c3736_ro')
user_1_ud = user_factory('db_1', name='tmp$c3736_ud', password='tmp$c3736_ud')

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, user_1_ro: User, user_1_ud: User):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

