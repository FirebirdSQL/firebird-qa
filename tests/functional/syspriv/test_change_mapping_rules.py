#coding:utf-8

"""
ID:          syspriv.change-mapping-rules
TITLE:       Check ability to manage auth mappings
DESCRIPTION:
  Verify ability to issue CREATE / ALTER / DROP MAPPING by non-sysdba user.
FBTEST:      functional.syspriv.change_mapping_rules
"""

import pytest
from firebird.qa import *

db = db_factory()

test_user = user_factory('db', name='john_smith_mapping_manager', do_not_create=True)
test_role = role_factory('db', name='tmp_role_for_change_mapping', do_not_create=True)

test_script = """
    set wng off;
    -- set bail on;
    set list on;

    -- NB: without 'grant admin role' it is unable to create GLOBAL mapping:
    -- Statement failed, SQLSTATE = 28000 / ... / -CREATE OR ALTER MAPPING ... failed
    -- -Unable to perform operation /-System privilege CHANGE_MAPPING_RULES is missing
    create or alter
         user john_smith_mapping_manager
         password '123'
         grant admin role --- [ !!! ]
    ;

    set term ^;
    execute block as
    begin
        execute statement 'drop role tmp_role_for_change_mapping';
        when any do begin end
    end^
    set term ;^

    create role tmp_role_for_change_mapping set system privileges to CHANGE_MAPPING_RULES;
    commit;

    grant default tmp_role_for_change_mapping to user john_smith_mapping_manager;
    commit;

    connect '$(DSN)' user john_smith_mapping_manager password '123'; --  role tmp_role_for_change_mapping;

    create or alter mapping tmp_syspriv_local_map using plugin srp from any user to user;
    create or alter global mapping tmp_syspriv_global_map using plugin srp from any user to user;
    commit;

    show mapping;

    drop global mapping tmp_syspriv_global_map;
    drop mapping tmp_syspriv_local_map;
    commit;

    --connect '$(DSN)' user sysdba password 'masterkey';
    --drop user john_smith_mapping_manager;
    --drop role tmp_role_for_change_mapping;
    --commit;
"""

act = isql_act('db', test_script, substitutions=[('.*Global mapping.*', '')])

expected_stdout = """
    TMP_SYSPRIV_LOCAL_MAP USING PLUGIN SRP FROM ANY USER TO USER
    *** Global mapping ***
    TMP_SYSPRIV_GLOBAL_MAP USING PLUGIN SRP FROM ANY USER TO USER
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action, test_user, test_role):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
