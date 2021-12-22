#coding:utf-8
#
# id:           bugs.core_3360
# title:        update ... returning ... raises -551 (no perm to update) for a column present only in the returning clause
# decription:   
# tracker_id:   CORE-3360
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
    set list on;
    set wng off;

    -- Drop old account with name = 'tmp$c3360' if it remains from prevoius run:
    set term ^;
    execute block as
    begin
        begin
        execute statement 'drop user tmp$c3360' with autonomous transaction;
            when any do begin end
        end
    end^
    set term ;^
    commit;

    create user tmp$c3360 password '123';
    commit;
    revoke all on all from tmp$c3360;
    commit;
    
    recreate table test(id int, readonly_x int, readonly_y int, writeable_column int); 
    commit;

    insert into test(id, readonly_x, readonly_y, writeable_column) values(1, 100, 200, 300); 
    commit;

    grant select on test to tmp$c3360;
    grant update (writeable_column) on test to tmp$c3360;
    commit;  

    connect '$(DSN)' user 'TMP$C3360' password '123';

    update test set writeable_column = readonly_x - readonly_y where id = 1 returning writeable_column;
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    drop user tmp$c3360;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WRITEABLE_COLUMN                -100
"""

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

