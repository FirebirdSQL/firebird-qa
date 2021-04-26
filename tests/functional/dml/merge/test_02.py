#coding:utf-8
#
# id:           functional.dml.merge.02
# title:        merge STATEMENT can have only one RETURNING after all WHEN sub-statements.
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

    -- [ 1 ] must PASS:
    merge into tb t
    using ta s on s.id = t.id
    when NOT matched then insert values(1,2,3) ---------------- (a)
    when matched then delete returning old.id, old.x, old.y --- (b)
    ;
    rollback;

    -- [ 2 ] must FAIL with
    -- Statement failed, SQLSTATE = 42000 / ... / -Token unknown / -when

    merge into tb t
    using ta s on s.id = t.id
    when matched then delete returning old.id, old.x, old.y --- (b)
    when NOT matched then insert values(1,2,3) ---------------- (a)
    ;

    rollback; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              <null>
    X                               <null>
    Y                               <null>
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 4, column 5
    -when
  """

@pytest.mark.version('>=3.0')
def test_02_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

