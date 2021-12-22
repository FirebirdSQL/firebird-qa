#coding:utf-8
#
# id:           functional.syspriv.modify_ext_conn_pool
# title:        Check ability to manage extyernal connections pool
# decription:   
#                  Verify ability to issue ALTER EXTERNAL CONNECTIONS POOL <...> by non-sysdba user.
#                  Checked  on 5.0.0.133 SS/CS, 4.0.1.2563 SS/CS
#                
# tracker_id:   
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set wng off;
    set list on;

    create or alter
         user john_smith_extpool_manager
         password '123'
    ;

    set term ^;
    execute block as
    begin
        execute statement 'drop role tmp_role_for_change_extpool';
        when any do begin end
    end^
    set term ;^

    create role tmp_role_for_change_extpool set system privileges to MODIFY_EXT_CONN_POOL;
    commit;

    grant default tmp_role_for_change_extpool to user john_smith_extpool_manager;
    commit;

    connect '$(DSN)' user john_smith_extpool_manager password '123';

    alter external connections pool set size 345;
    alter external connections pool set lifetime 789 second;
    commit;

    select 
        cast(rdb$get_context('SYSTEM', 'EXT_CONN_POOL_SIZE') as int) as pool_size,
        cast(rdb$get_context('SYSTEM', 'EXT_CONN_POOL_LIFETIME') as int) as pool_lifetime
    from rdb$database;
    rollback;

    connect '$(DSN)' user sysdba password 'masterkey';
    drop user john_smith_extpool_manager;
    drop role tmp_role_for_change_extpool;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    POOL_SIZE                       345
    POOL_LIFETIME                   789
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

