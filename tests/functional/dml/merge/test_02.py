#coding:utf-8
#
# id:           functional.dml.merge.02
# title:        merge STATEMENT can have only one RETURNING which must be after all WHEN sub-statements.
# decription:   
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('-Token unknown .*', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    recreate table ta(id int primary key, x int, y int);
    recreate table tb(id int primary key, x int, y int);
    commit;
    
    insert into ta(id, x, y) values(1, 10, 100);
    insert into tb(id, x, y) values(1, 10, 100);
    commit;

    -- [ 1 ] must PASS:
    merge into tb t
    using ta s on s.id = t.id
    when NOT matched then insert values(-s.id, -s.x, -s.y) ------------------------- (a)
    when matched then
        delete
        returning old.id as deleted_id, old.x as deleted_x, old.y as deleted_y ----- (b)
    ;
    rollback;

    -- [ 2 ] must FAIL with
    -- Statement failed, SQLSTATE = 42000 / ... / -Token unknown / -when

    merge into tb t
    using ta s on s.id = t.id
    when matched then delete returning old.id, old.x, old.y ----------------------- (b)
    when NOT matched then insert values(-s.id, -s.x, -s.y) ------------------------ (a)
    ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DELETED_ID                      1
    DELETED_X                       10
    DELETED_Y                       100
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 4, column 5
    -when
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

    assert act_1.clean_stdout == act_1.clean_expected_stdout

