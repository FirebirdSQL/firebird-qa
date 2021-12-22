#coding:utf-8
#
# id:           bugs.core_2731
# title:        Recursive EXECUTE STATEMENT works wrong
# decription:   
#                   Checked on:
#                       4.0.0.1635 SS: 2.030s.
#                       4.0.0.1633 CS: 5.765s.
#                       3.0.5.33180 SS: 3.016s.
#                       3.0.5.33178 CS: 4.001s.
#                       2.5.9.27119 SS: 0.519s.
#                       2.5.9.27146 SC: 0.965s.
#                
# tracker_id:   CORE-2731
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('[-]{0,1}At block line: [\\d]+, col: [\\d]+', '')]

init_script_1 = """
    recreate table SQL_SOURCE(
        SQL_SOURCE varchar(32000)
    );
    commit;

    insert into SQL_SOURCE values(
        'execute block as
        declare variable SQL type of column SQL_SOURCE.SQL_SOURCE;
        begin
            select first(1) SQL_SOURCE from SQL_SOURCE into :SQL;
            execute statement :SQL
            -- YOUR DB
            on external ''$(DSN)''
            as user ''SYSDBA'' password ''masterkey'';
        end'
    );
    commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^ ;
    execute block as
        declare v_sql type of column SQL_SOURCE.SQL_SOURCE;
    begin
        select first(1) SQL_SOURCE from SQL_SOURCE into :v_sql;
        execute statement :v_sql;
    end ^
    set term ; ^
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

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement error at isc_dsql_execute2 :
    335544926 : Execute statement...
    -At block line: 5, col: 5
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

