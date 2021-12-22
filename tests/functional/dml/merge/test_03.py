#coding:utf-8
#
# id:           functional.dml.merge.03
# title:        MERGE ... RETURNING must refer either ALIAS of the table (if it is defined) or context variables OLD and NEW
# decription:   
#                   Checked on 4.0.0.2240
#                
# tracker_id:   
# min_versions: []
# versions:     4.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('-At line .*', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    recreate table test_a(id int primary key, x int);
    recreate table test_b(id int primary key, x int);
    commit;
    insert into test_a(id, x) values(1, 100);
    insert into test_b(id, x) values(1, 100);
    commit;

    --set echo on;

    -- [ 1 ] must FAIL with "SQLSTATE = 42S22 / ... / -Column unknown -TEST_B.ID"
    merge into test_b t
    using test_a s on s.id = t.id
    when matched then
        delete returning test_b.id, test_b.x
    ;

    rollback; 

    -- [ 2 ] must PASS:
    merge into test_b t
    using test_a s on s.id = t.id
    when matched then
        delete
        returning old.id as old_id, t.x as old_t_x
    ;

    rollback;

    -- [ 3 ] must PASS:
    merge into test_b t
    using test_a s on s.id = t.id
    when matched then
        update set t.id = -s.id - 1, t.x = - s.x - 1
        returning old.id as old_id, old.x as old_x, new.id as new_id, t.x as new_x
    ;

    rollback;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    OLD_ID                          1
    OLD_T_X                         100

    OLD_ID                          1
    OLD_X                           100
    NEW_ID                          -2
    NEW_X                           -101
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -TEST_B.ID
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

    assert act_1.clean_stdout == act_1.clean_expected_stdout

