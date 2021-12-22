#coding:utf-8
#
# id:           bugs.core_0927
# title:        Grants don't work for procedures used inside views
# decription:   
#                   Checked on: 4.0.0.1635: OK, 2.209s; 3.0.5.33180: OK, 1.838s; 2.5.9.27119: OK, 0.292s.
#                
# tracker_id:   CORE-927
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set wng off;
    set list on;

    -- Drop old account if it remains from prevoius run:
    set term ^;
    execute block as
    begin
        begin
        execute statement 'drop user tmp$c0927' with autonomous transaction;
            when any do begin end
        end
    end^
    set term ;^
    commit;

    create user tmp$c0927 password '123';
    commit;
    revoke all on all from tmp$c0927;
    commit;
    
    create or alter view v_test as select 1 id from rdb$database;
    commit;
    
    set term ^;
    create or alter procedure sp_test returns (result integer) as
    begin
        result = 1;
        suspend;
    end
    ^
    set term ;^
    commit;
    
    create or alter view v_test as
    select (select result from sp_test) as result from rdb$database;
    
    grant execute on procedure sp_test to view v_test;
    grant select on v_test to tmp$c0927;
    commit;

    -------------------------------------------------
    connect '$(DSN)' user 'tmp$c0927' password '123';
    -------------------------------------------------
    select current_user as who_am_i, v.* from v_test v;
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';

    drop user tmp$c0927;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WHO_AM_I                        TMP$C0927
    RESULT                          1
"""

@pytest.mark.version('>=2.5.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

