#coding:utf-8
#
# id:           functional.dml.delete.02
# title:        DELETE with WHERE
# decription:   
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.dml.delete.delete_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE tb(id INT);
INSERT INTO tb VALUES(10);
INSERT INTO tb VALUES(10);
INSERT INTO tb VALUES(20);
COMMIT;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """DELETE FROM tb WHERE id>10;
SELECT * FROM tb;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """          ID
============

          10
10"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

