#coding:utf-8
#
# id:           bugs.core_0606
# title:         Tricky role defeats basic SQL security
# decription:   
#                   CHecked on:
#                       4.0.0.1635 SS: 1.482s.
#                       4.0.0.1633 CS: 1.954s.
#                       3.0.5.33180 SS: 0.976s.
#                       3.0.5.33178 CS: 1.265s.
#                       2.5.9.27119 SS: 0.297s.
#                       2.5.9.27146 SC: 0.306s.
#                
# tracker_id:   CORE-0606
# min_versions: ['2.5']
# versions:     2.5.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.6
# resources: None

substitutions_1 = [('Statement failed, SQLSTATE = HY000', ''), ('record not found for user:.*', ''), ('read/select', 'SELECT'), ('Data source : Firebird::.*', 'Data source : Firebird::'), ('-At block line: [\\d]+, col: [\\d]+', '-At block line'), ('335545254 : Effective user is.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    execute block as
    begin
        begin
            execute statement 'drop role "FOR CVC"';
        when any do begin end
        end
        begin
            execute statement 'drop role "FOR"';
        when any do begin end
        end
    end
    ^set term ;^
    commit;

    drop user cvc;
    commit;

    recreate table "t t"(data int);
    commit;
    insert into "t t" values(123456);
    commit;

    create user cvc password 'pw';
    commit;

    create role "FOR CVC";
    create role "FOR";

    grant "FOR CVC" to user cvc;
    grant select on table "t t" to "FOR";
    commit;

    show grants;
    commit;
    
    set list on;
    set term ^;
    execute block returns(who_am_i varchar(31), i_m_playing_role varchar(31)) as
    begin
      for 
         execute statement 'select current_user, current_role from rdb$database'
         on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
         as user 'cvc' password 'pw' role '"FOR CVC"'
         into who_am_i, i_m_playing_role
      do
         suspend;
    end
    ^
    
    execute block returns(data int) as
    begin
      for 
         execute statement 'select data from "t t"'
         on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
         as user 'cvc' password 'pw' role '"FOR CVC"'
         into data
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

    drop user cvc;
    commit;
    drop role "FOR CVC";
    drop role "FOR";
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    /* Grant permissions for this database */
    GRANT SELECT ON t t TO ROLE FOR
    GRANT FOR CVC TO CVC
    
    WHO_AM_I                        CVC
    I_M_PLAYING_ROLE                FOR CVC
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Execute statement error at isc_dsql_prepare :
    335544352 : no permission for SELECT access to TABLE t t
    Statement : select data from "t t"
    Data source : Firebird::localhost:C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\E30.FDB
    -At block line: 3, col: 7
  """

@pytest.mark.version('>=2.5.6')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

