#coding:utf-8

"""
ID:          issue-4488
ISSUE:       4488
TITLE:       User can not insert records into table with column "generated by default as identity" in its DDL
DESCRIPTION:
JIRA:        CORE-4161
FBTEST:      bugs.core_4161
"""

import pytest
from firebird.qa import *

db = db_factory()
tmp_user = user_factory('db', name='tmp$core4161', password='123')

test_script = """
    set wng off;
    set list on;

    recreate table autoid_test(id int generated by default as identity primary key, f01 int);
    insert into autoid_test(f01) values(100);
    insert into autoid_test(f01) values(200);
    insert into autoid_test(f01) values(300);
    commit;

    recreate table backup_data(id int, f01 int);
    insert into backup_data(id, f01) select id, f01 from autoid_test;
    commit;

    grant insert,update,delete,select on autoid_test to tmp$core4161;
    grant select on backup_data to tmp$core4161;
    commit;

    set term ^;
    execute block returns( who_am_i type of column sec$users.sec$user_name, mine_id int, mine_f01 int )
    as
      declare v_dbname type of column mon$database.mon$database_name;
      declare v_usr type of column sec$users.sec$user_name = 'tmp$core4161';
      declare v_pwd varchar(20) = '123';
      declare v_connect varchar(255);
      declare v_dummy int;
    begin
      select 'localhost:' || d.mon$database_name
      from mon$database d
      into v_dbname;

      execute statement 'select count(*) from autoid_test'
      on external (v_dbname)
      as user (v_usr) password (v_pwd)
      into v_dummy;

      execute statement ('update autoid_test set f01=-f01 where id = :x') (x := 1)
      on external (v_dbname)
      as user (v_usr) password (v_pwd);

      execute statement ('delete from autoid_test where id >= :x') (x := 1)
      on external (v_dbname)
      as user (v_usr) password (v_pwd);

      execute statement ('insert into autoid_test(f01) values(:x)') (x := 555)
      on external (v_dbname)
      as user (v_usr) password (v_pwd);

      execute statement ('insert into autoid_test(id, f01) values(:i, :x)') (i := -1,  x := -555)
      on external (v_dbname)
      as user (v_usr) password (v_pwd);

      execute statement ('insert into autoid_test(f01) select f01 from backup_data')
      on external (v_dbname)
      as user (v_usr) password (v_pwd);

      for
        execute statement 'select current_user, id, f01 from autoid_test'
        on external (v_dbname)
        as user (v_usr) password (v_pwd)
        into who_am_i, mine_id, mine_f01
      do
        suspend;

    end
    ^
    set term ;^
    rollback;

    select current_user as who_am_i, id as mine_id, f01 as mine_f01
    from autoid_test;
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

act = isql_act('db', test_script)

expected_stdout = """
    WHO_AM_I                        TMP$CORE4161
    MINE_ID                         4
    MINE_F01                        555

    WHO_AM_I                        TMP$CORE4161
    MINE_ID                         -1
    MINE_F01                        -555

    WHO_AM_I                        TMP$CORE4161
    MINE_ID                         5
    MINE_F01                        100

    WHO_AM_I                        TMP$CORE4161
    MINE_ID                         6
    MINE_F01                        200

    WHO_AM_I                        TMP$CORE4161
    MINE_ID                         7
    MINE_F01                        300



    WHO_AM_I                        SYSDBA
    MINE_ID                         1
    MINE_F01                        100

    WHO_AM_I                        SYSDBA
    MINE_ID                         2
    MINE_F01                        200

    WHO_AM_I                        SYSDBA
    MINE_ID                         3
    MINE_F01                        300
"""

@pytest.mark.es_eds
@pytest.mark.version('>=3.0')
def test_1(act: Action, tmp_user: User):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

