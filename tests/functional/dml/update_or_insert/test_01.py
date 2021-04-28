#coding:utf-8
#
# id:           functional.dml.update_or_insert.01
# title:        UPDATE OR INSERT
# decription:   Simple UPDATE OR INSERT
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.dml.update_or_insert.update_or_insert_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TMPTEST( id INTEGER , name VARCHAR(20) , PRIMARY KEY(id));"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """UPDATE OR INSERT INTO TMPTEST(id, name) VALUES (1,'bob' );
select name from TMPTEST where id =1;
UPDATE OR INSERT INTO TMPTEST(id, name) VALUES (1,'ivan' );
select name from TMPTEST where id =1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
NAME
====================
bob


NAME
====================
ivan

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

