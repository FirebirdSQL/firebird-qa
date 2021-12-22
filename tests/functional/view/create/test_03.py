#coding:utf-8
#
# id:           functional.view.create.03
# title:        CREATE VIEW - bad number of columns
# decription:   CREATE VIEW - bad number of columns
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.view.create.create_view_03

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE tb(id INT);
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE VIEW test (id,num,text) AS SELECT id,5 FROM tb;
SHOW VIEW test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 07002
unsuccessful metadata update
-CREATE VIEW TEST failed
-SQL error code = -607
-Invalid command
-number of columns does not match select list
There is no view TEST in this database"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

