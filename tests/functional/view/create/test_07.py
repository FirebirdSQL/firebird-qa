#coding:utf-8
#
# id:           functional.view.create.07
# title:        CREATE VIEW - updateable WITH CHECK OPTION
# decription:   CREATE VIEW - updateable WITH CHECK OPTION
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.view.create.create_view_07

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE tb(id INT);"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE VIEW test (id) AS SELECT id FROM tb WHERE id<10 WITH CHECK OPTION;
INSERT INTO test VALUES(2);
COMMIT;
SELECT * FROM test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """          ID
============

           2
"""

@pytest.mark.version('>=1.0')
def test_07_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

