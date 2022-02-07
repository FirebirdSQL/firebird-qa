#coding:utf-8

"""
ID:          issue-6392
ISSUE:       6392
TITLE:       Error 'Multiple maps found for ...' is raised in not appropriate case
DESCRIPTION:
  There was issue about mapping of ROLES: currently mapping can be done only for trusted role.
  But documentation does not mention about this. One can conclude that mapping should work
  as for trusted role and also for "usual" way (i.e. when used specifies 'ROLE ...' clause).
  Discussion about this with Alex was in 23-sep-2019, and his solution not yet known.
  For this reason it was decided to comment code that relates tgo ROLE mapping in this test.
NOTES:
[3.11.2021] pcisar
  This test fails for 4.0, WHO_AM_I = TMP$C6143_FOO instead TMP$C6143_RIO
JIRA:        CORE-6143
FBTEST:      bugs.core_6143
"""

import pytest
from firebird.qa import *

db = db_factory()

user_foo = user_factory('db', name='tmp$c6143_foo', password='123', plugin='Srp')
role_boss = role_factory('db', name='tmp$r6143_boss')

test_script = """
    -- set echo on;
    set list on;
    set wng off;

    create or alter view v_show_mapping as
    select
         a.rdb$map_name
        ,a.rdb$map_using
        ,a.rdb$map_plugin
        ,a.rdb$map_db
        ,a.rdb$map_from_type
        ,a.rdb$map_from
        ,a.rdb$map_to_type
        ,a.rdb$map_to
    from rdb$database d
    left join rdb$auth_mapping a on 1=1
    where rdb$map_from containing 'tmp$c6143' or rdb$map_from containing 'tmp$r6143'
    ;
    commit;
    grant select on v_show_mapping to public;

    --create or alter user tmp$c6143_foo password '123' using plugin Srp;
    --commit;
    --revoke all on all from tmp$c6143_foo;
    --commit;

    --create role tmp$r6143_boss;
    --commit;

    -- ++++++++++++++++++++++++ T E S T    L O C A L    M A P P I N G  +++++++++++++++++++++++


    create or alter mapping lmap_foo2bar_a using plugin srp from user tmp$c6143_foo to user tmp$c6143_bar;
    create or alter mapping lmap_foo2bar_b using plugin srp from user tmp$c6143_foo to user tmp$c6143_bar;

    create or alter mapping lmap_boss2acnt_a using plugin srp from role tmp$r6143_boss to role tmp$r6143_acnt;
    create or alter mapping lmap_boss2acnt_b using plugin srp from role tmp$c6143_boss to role tmp$r6143_acnt;
    commit;

    grant tmp$r6143_boss to user tmp$c6143_bar;
    commit;


    connect '$(DSN)' user tmp$c6143_foo password '123' role tmp$r6143_boss;
    select
        'Connected OK when local mapping is duplicated.' as msg
        ,current_user as who_am_i     -- <<< TMP$C6143_BAR must be shown here, *NOT* tmp$c6143_foo
        -- temply disabled, wait for solution by Alex, see letters to him 23.09.2019 12:02:
        -- ,current_role as what_my_role -- <<< WHAT ROLE MUST BE SHOWN HERE, *BOSS or *ACNT ???
    from rdb$database;

    set count on;
    select * from v_show_mapping;
    set count on;
    commit;


    connect '$(DSN)' user sysdba password 'masterkey';
    commit;
    drop mapping lmap_foo2bar_a;
    drop mapping lmap_foo2bar_b;
    drop mapping lmap_boss2acnt_a;
    drop mapping lmap_boss2acnt_b;
    commit;

    -- ++++++++++++++++++++++++ T E S T    G L O B A L    M A P P I N G  +++++++++++++++++++++++


    create or alter global mapping gmap_foo2rio_a using plugin srp from user tmp$c6143_foo to user tmp$c6143_rio;
    create or alter global mapping gmap_foo2rio_b using plugin srp from user tmp$c6143_foo to user tmp$c6143_rio;

    create or alter global mapping gmap_boss2mngr_a using plugin srp from role tmp$r6143_boss to role tmp$r6143_mngr;
    create or alter global mapping gmap_boss2mngr_b using plugin srp from role tmp$c6143_boss to role tmp$r6143_mngr;
    commit;

    connect '$(DSN)' user tmp$c6143_foo password '123' role tmp$r6143_boss;
    select
        'Connected OK when global mapping is duplicated.' as msg
        ,current_user as who_am_i     -- <<< TMP$C6143_RIO must be shown here, *NOT* tmp$c6143_foo
        -- temply diabled, wait for solution by Alex, see letters to him 23.09.2019 12:02:
        -- ,current_role as what_my_role -- <<< WHAT ROLE MUST BE SHOWN HERE, *BOSS or *MNGR or... NONE ???
    from rdb$database;
    commit;


    connect '$(DSN)' user sysdba password 'masterkey';
    commit;
    drop global mapping gmap_foo2rio_a;
    drop global mapping gmap_foo2rio_b;
    drop global mapping gmap_boss2mngr_a;
    drop global mapping gmap_boss2mngr_b;
    commit;
"""

act = isql_act('db', test_script)

expected_stdout = """
    MSG                             Connected OK when local mapping is duplicated.
    WHO_AM_I                        TMP$C6143_BAR

    RDB$MAP_NAME                    LMAP_FOO2BAR_A
    RDB$MAP_USING                   P
    RDB$MAP_PLUGIN                  SRP
    RDB$MAP_DB                      <null>
    RDB$MAP_FROM_TYPE               USER
    RDB$MAP_FROM                    TMP$C6143_FOO
    RDB$MAP_TO_TYPE                 0
    RDB$MAP_TO                      TMP$C6143_BAR

    RDB$MAP_NAME                    LMAP_FOO2BAR_B
    RDB$MAP_USING                   P
    RDB$MAP_PLUGIN                  SRP
    RDB$MAP_DB                      <null>
    RDB$MAP_FROM_TYPE               USER
    RDB$MAP_FROM                    TMP$C6143_FOO
    RDB$MAP_TO_TYPE                 0
    RDB$MAP_TO                      TMP$C6143_BAR

    RDB$MAP_NAME                    LMAP_BOSS2ACNT_A
    RDB$MAP_USING                   P
    RDB$MAP_PLUGIN                  SRP
    RDB$MAP_DB                      <null>
    RDB$MAP_FROM_TYPE               ROLE
    RDB$MAP_FROM                    TMP$R6143_BOSS
    RDB$MAP_TO_TYPE                 1
    RDB$MAP_TO                      TMP$R6143_ACNT

    RDB$MAP_NAME                    LMAP_BOSS2ACNT_B
    RDB$MAP_USING                   P
    RDB$MAP_PLUGIN                  SRP
    RDB$MAP_DB                      <null>
    RDB$MAP_FROM_TYPE               ROLE
    RDB$MAP_FROM                    TMP$C6143_BOSS
    RDB$MAP_TO_TYPE                 1
    RDB$MAP_TO                      TMP$R6143_ACNT

    Records affected: 4

    MSG                             Connected OK when global mapping is duplicated.
    WHO_AM_I                        TMP$C6143_RIO

    Records affected: 1
"""

@pytest.mark.version('>=3.0.5,<4')
def test_1(act: Action, role_boss: Role, user_foo: User):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

@pytest.mark.skip("FIXME: see notes")
@pytest.mark.version('>=4')
def test_1(act: Action, role_boss: Role, user_foo: User):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
