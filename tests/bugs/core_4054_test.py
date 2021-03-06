#coding:utf-8
#
# id:           bugs.core_4054
# title:        role not passed on external execute stmt
# decription:   
#                   Checked on:
#                       4.0.0.1635 SS: 1.359s.
#                       4.0.0.1633 CS: 1.832s.
#                       3.0.5.33180 SS: 0.879s.
#                       3.0.5.33178 CS: 1.221s.
#                       2.5.9.27119 SS: 0.272s.
#                       2.5.9.27146 SC: 0.290s.
#                
# tracker_id:   CORE-4054
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set wng off;
    -- Drop old account if it remains from prevoius run:
    set term ^;
    execute block as
    begin
        begin
            execute statement 'drop user tmp$c4054' with autonomous transaction;
            when any do begin end
        end
    end
    ^
    set term ;^
    commit;

    create user tmp$c4054 password '123';
    commit;
    revoke all on all from tmp$c4054;
    commit;

    create table test(id int);
    commit;
    insert into test(id) values(789654123);
    commit;

    set term ^;
    execute block as
    begin
        execute statement 'drop role r4054';
    when any do
        begin
        end
    end
    ^
    set term ;^
    commit;
    create role r4054;
    commit;
    
    
    grant select on test to role r4054;
    commit;
    
    grant r4054 to tmp$c4054;
    commit;
    
    set list on;
    set term ^;
    execute block returns (who_am_i varchar(30), whats_my_role varchar(30), what_i_see int) as
        declare v_dbname type of column mon$database.mon$database_name;
        declare v_usr rdb$user = 'tmp$c4054';
        declare v_pwd rdb$user = '123';
        declare v_role type of column rdb$roles.rdb$role_name;
    begin
        v_dbname = 'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME');

        --######################
        v_role = upper('r4054'); -- !!! ACHTUNG !!! ROLE NAME MUST BE ALWAYS PASSED IN UPPER CASE !!!
        --######################
        -- Explanation can be seen here (russian):
        -- http://www.sql.ru/forum/actualutils.aspx?action=gotomsg&tid=1074439&msg=15494916
        for
            execute statement 'select current_user, current_role, t.id from test t'
            on external v_dbname
            as user v_usr 
               password v_pwd 
               role v_role -- ####### ONCE AGAIN: ALWAYS PASS ROLE NAME IN *UPPER* CASE! ##########
            into who_am_i, whats_my_role, what_i_see
        do
            suspend;
    end
    ^
    set term ;^
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

    -- Do not forget about cleanup - remember that other tests can query sec$users or run `show users`!
    drop user tmp$c4054;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WHO_AM_I                        TMP$C4054
    WHATS_MY_ROLE                   R4054
    WHAT_I_SEE                      789654123
  """

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

