#coding:utf-8
#
# id:           bugs.core_5555
# title:        3.0 error handling for SELECT WITH LOCK breaks compatibility with 2.5
# decription:   
#                   Checked on:
#                       4.0.0.1635 SS: OK, 1.053s.
#                       4.0.0.1633 CS: OK, 1.309s.
#                       3.0.5.33180 SS: OK, 0.823s.
#                       3.0.5.33178 CS: OK, 1.181s.
#                   See also http://tracker.firebirdsql.org/browse/CORE-4473
#                
# tracker_id:   CORE-5555
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    recreate table test(x int, y int);
    insert into test(x, y) values(1, 2);
    commit;

    set transaction no wait;

    set term ^;
    execute block as
      declare c int;
    begin
      execute statement ('select current_transaction from test where x = ? and 1=1 with lock') (1) 
          on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
          as user 'sysdba' password 'masterkey'
      into c;
    end
    ^

    execute block returns(gds_on_update int) as
    begin
        begin
            update test set y = -y where x = 1 and 2=2;
        when any do
            begin
                gds_on_update = gdscode;
            end
        end
        suspend;
    end
    ^

    execute block returns(gds_on_select_with_lock int) as
        declare c int;
    begin
        begin
            select y from test where x = 1 and 3=3 with lock into c;
        when any do
            begin
                gds_on_select_with_lock = gdscode;
            end
        end
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
    GDS_ON_UPDATE                   335544336
    GDS_ON_SELECT_WITH_LOCK         335544336
  """

@pytest.mark.version('>=3.0.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

