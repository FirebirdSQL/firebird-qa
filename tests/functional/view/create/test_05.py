#coding:utf-8
#
# id:           functional.view.create.05
# title:        CREATE VIEW
# decription:   CREATE VIEW
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               INSERT
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.view.create.create_view_05

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE tb(id INT);
INSERT INTO tb VALUES(3);
INSERT INTO tb VALUES(10);
COMMIT;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE VIEW test (id,num) AS SELECT id,5 FROM tb;
SELECT * FROM test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """          ID          NUM
============ ============

           3            5
          10            5
"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

