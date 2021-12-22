#coding:utf-8
#
# id:           bugs.core_1292
# title:        Can't create table using long username and UTF8 as attachment charset
# decription:   
#                   Checked on: 4.0.0.1635 SS/CS; 3.0.5.33180 SS/CS; 2.5.9.27119 SC/SS
#                
# tracker_id:   CORE-1292
# min_versions: []
# versions:     2.5
# qmid:         bugs.core_1292

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('PRIV_LIST.*', '')]

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    set wng off;

    -- Drop old account if it remains from prevoius run:
    set term ^;
    execute block as
    begin
        begin
        execute statement 'drop user Nebuchadnezzar2_King_of_Babylon' with autonomous transaction;
            when any do begin end
        end
    end^
    set term ;^
    commit;


    create user Nebuchadnezzar2_King_of_Babylon password 'guinness'; -- revoke admin role;
    --          1234567890123456789012345678901
    --                   1         2         3
    commit;
    revoke all on all from Nebuchadnezzar2_King_of_Babylon;
    set term ^;
    execute block as
    begin
        if ( rdb$get_context('SYSTEM', 'ENGINE_VERSION') not starting with '2.5' ) then
        begin
            execute statement 'grant create table to Nebuchadnezzar2_King_of_Babylon';
        end
    end
    ^
    set term ;^
    commit;

    connect '$(DSN)' user 'Nebuchadnezzar2_King_of_Babylon' password 'guinness';

    create table test(n int);
    commit;
    
    connect '$(DSN)' user 'SYSDBA' password 'masterkey';

    set list on;
    select usr_name, grantor, can_grant, tab_name,usr_type,obj_type, list(priv) priv_list
    from (
        select
            p.rdb$user usr_name
            ,p.rdb$grantor grantor
            ,p.rdb$grant_option can_grant
            ,p.rdb$relation_name tab_name
            ,p.rdb$user_type usr_type
            ,p.rdb$object_type obj_type
            ,trim(p.rdb$privilege) priv
        from rdb$user_privileges p
        where upper(trim(p.rdb$relation_name)) = upper('test')
        order by priv
    )
    group by usr_name, grantor, can_grant, tab_name,usr_type,obj_type;  
    commit;

    drop user Nebuchadnezzar2_King_of_Babylon;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    USR_NAME                        NEBUCHADNEZZAR2_KING_OF_BABYLON
    GRANTOR                         NEBUCHADNEZZAR2_KING_OF_BABYLON
    CAN_GRANT                       1
    TAB_NAME                        TEST
    USR_TYPE                        8
    OBJ_TYPE                        0
    D,I,R,S,U
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

