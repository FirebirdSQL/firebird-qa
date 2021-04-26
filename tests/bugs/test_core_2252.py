#coding:utf-8
#
# id:           bugs.core_2252
# title:        EXECUTE STATEMENT on EXTERNAL SOURCE does not check the status of the transaction
# decription:   
# tracker_id:   CORE-2252
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = [('Data source : Firebird.*', 'Data source : Firebird'), ('[-]{0,1}At block line: [\\d]+, col: [\\d]+', 'At block line')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set term ^;
    execute block returns (tran_id integer) as
    begin
        
        execute statement 'select sign(current_transaction) from rdb$database'
        on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
        as user 'sysdba' password 'masterkey'
        into :tran_id;
        
        suspend;
        
        execute statement 'commit'
        on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
        as user 'sysdba' password 'masterkey';
        
        execute statement 'select sign(current_transaction) from rdb$database'
        on external 'localhost:'  || rdb$get_context('SYSTEM','DB_NAME')
        as user 'sysdba' password 'masterkey'
        into :tran_id;
        
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
    TRAN_ID                         1
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Execute statement error at isc_dsql_prepare :
    335544986 : Explicit transaction control is not allowed
    Statement : commit
    Data source : Firebird::localhost:C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\BUGS.CORE_2252.FDB
    -At block line: 11, col: 9
  """

@pytest.mark.version('>=2.5.0')
def test_core_2252_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

