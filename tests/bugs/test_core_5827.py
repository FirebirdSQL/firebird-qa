#coding:utf-8
#
# id:           bugs.core_5827
# title:        ALTER CURRENT USER fails with "no permission for <...> TABLE PLG$SRP" if current user: 1) has NO admin role and 2) wants to modify his own TAGS list
# decription:   
#                   ::: NB :::
#                   Code of this test must to be changed after ticket will be fixed!
#                   See line with 'grant admin role' -- it must me COMMENTED.
#                   Also, min_version should be set to 3.0.x rather than 4.0.0
#               
#                   Currently we check only ability to change TAGS list using 'ALTER CURRENT USER' statement.
#                   See also test for CORE-3365, but it checks only 'old' attributes which existed before FB 3.0.
#                 
# tracker_id:   CORE-5827
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
    set bail on;
    set list on;

    set term ^;
    execute block as
    begin
        begin
        execute statement 'drop user tmp$c5827 using plugin Srp' with autonomous transaction;
            when any do begin end
        end
    end^
    set term ;^
    commit;

    --set echo on;

    create user tmp$c5827
        password 'UseSrp'
        firstname 'Mary'

    -- NB: no error will be raised if we UNCOMMENT this line; IMO this is bug, see ticket issue; 
    -- TODO: comment must be here, put it later when this ticket issue will be fixed.
    grant admin role

    using plugin Srp
        tags (
             key1 = 'val111'
            ,key2 = 'val222'
            ,key3 = 'val333'
        )
    ;
    commit;

    connect '$(DSN)' user tmp$c5827 password 'UseSrp';

    --- passed w/o error:
    alter current user
        set password 'FooSrp' firstname 'Scott' lastname 'Tiger'
        using plugin Srp
    ;
    commit;

    -- DOES raise error if current user has no admin role:
    alter current user
        using plugin Srp
        tags (
             Foo = 'Bar'
            ,key1 = 'val11'
            ,Rio = '1565'
            ,drop key3
            ,drop key2
        )
    ; 
    commit;

    -- cleanup:
    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    drop user tmp$c5827 using plugin Srp;
    commit;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=4.0')
def test_core_5827_1(act_1: Action):
    act_1.execute()

