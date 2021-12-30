#coding:utf-8
#
# id:           bugs.gh_6732
# title:        Stored procedure isn't able to execute statement 'GRANT' [CORE6502]
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6732
#               
#                   Confirmed bug on 4.0.0.2453, got:
#                       Statement failed, SQLSTATE = 27000
#                       unsuccessful metadata update
#                       -GRANT failed
#                       -action cancelled by trigger (0) to preserve data integrity
#                       -User cannot write to RDB$USER_PRIVILEGES
#                       -At procedure 'SP_TEST' line: 3, col: 8
#               
#                   ::: NB ::: 22.05.2021
#                   This test initially had wrong value of min_version = 4.0
#                   Bug was fixed on 4.1.0.2468, build timestamp: 06-may-2021 12:34 thus min_version should be 4.1
#                   After several days this new FB branch was renamed to 5.0.
#                   Because of this, min_version for this test is 5.0
#                
# tracker_id:   
# min_versions: ['5.0']
# versions:     5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter user tmp$gh6732_boss password 'boss' using plugin Srp;
    create or alter user tmp$gh6732_acnt password 'acnt' using plugin Srp;
    commit;

    set term ^;
    create or alter procedure sp_test SQL SECURITY DEFINER as
    begin
       execute statement 'grant alter any generator to tmp$gh6732_acnt';
    end
    ^
    set term ;^
    commit;
    grant execute on procedure sp_test to user tmp$gh6732_boss;
    commit;

    connect '$(DSN)' user tmp$gh6732_boss password 'boss';
    execute procedure sp_test; -- must NOT raise error.
    commit;

    -- cleanup:
    connect '$(DSN)' user sysdba password 'masterkey';
    drop user tmp$gh6732_boss using plugin Srp;
    drop user tmp$gh6732_acnt using plugin Srp;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=5.0')
def test_1(act_1: Action):
    act_1.execute()
