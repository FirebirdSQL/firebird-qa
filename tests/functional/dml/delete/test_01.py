#coding:utf-8
#
# id:           functional.dml.delete.01
# title:        DELETE
# decription:   
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.dml.delete.delete_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE tb(id INT);
INSERT INTO tb VALUES(10);
COMMIT;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """DELETE FROM tb;
SELECT * FROM tb;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.execute()

