#coding:utf-8
#
# id:           functional.view.create.08
# title:        CREATE VIEW - updateable WITH CHECK OPTION
# decription:   CREATE VIEW - updateable WITH CHECK OPTION
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.view.create.create_view_08

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('-At trigger.*', '')]

init_script_1 = """CREATE TABLE tb(id INT);
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE VIEW test (id) AS SELECT id FROM tb WHERE id<10 WITH CHECK OPTION;
INSERT INTO test VALUES(10);"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 23000
Operation violates CHECK constraint  on view or table TEST
-At trigger 'CHECK_1'
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

