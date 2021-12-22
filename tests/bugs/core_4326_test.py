#coding:utf-8
#
# id:           bugs.core_4326
# title:        Keyword SET should not be required in ALTER USER statement
# decription:
#                   Checked on:
#                       4.0.0.1635 SS: OK, 1.555s.
#                       4.0.0.1633 CS: OK, 1.966s.
#                       3.0.5.33180 SS: OK, 0.970s.
#                       3.0.5.33178 CS: OK, 1.435s.
#
# tracker_id:   CORE-4326
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action, user_factory, User

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    alter user tmp$c4326 password '456' firstname 'Deep' lastname 'Purple';
    commit;

    create or alter view v_user_info as
    select sec$user_name uname, sec$first_name fname, sec$last_name lname from sec$users
    where sec$user_name = upper('tmp$c4326');
    commit;

    set list on;

    select * from v_user_info;

    commit;
    set transaction read committed;
    set term ^;
    execute block returns(
      uname type of column sec$users.sec$user_name
      ,fname type of column sec$users.sec$first_name
      ,lname type of column sec$users.sec$last_name
    )  as
      declare v_usr type of column sec$users.sec$user_name = 'tmp$c4326';
      declare v_pwd varchar(20) = '456';

    begin
      execute statement 'alter current user password ''IronMan'' firstname ''Black'' lastname ''Sabbath'''
      with autonomous transaction
      on external ( 'localhost:' || rdb$get_context('SYSTEM','DB_NAME') )
         as user v_usr password v_pwd;

      for select uname, fname, lname from v_user_info into uname, fname, lname do suspend;

      execute statement 'alter current user password ''Kashmir'' firstname ''Led'' lastname ''Zeppelin'''
      on external ( 'localhost:' || rdb$get_context('SYSTEM','DB_NAME') )
         as user v_usr password 'IronMan';

    end
    ^
    set term ;^
    commit;

    select * from v_user_info;
    commit;

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
    UNAME                           TMP$C4326
    FNAME                           Deep
    LNAME                           Purple

    UNAME                           TMP$C4326
    FNAME                           Black
    LNAME                           Sabbath

    UNAME                           TMP$C4326
    FNAME                           Led
    LNAME                           Zeppelin
"""

user_1 = user_factory('db_1', name='tmp$c4326', password='123')

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, user_1: User):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

