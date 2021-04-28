#coding:utf-8
#
# id:           functional.dml.update_or_insert.03
# title:        UPDATE OR INSERT
# decription:   MATCHING Clause
# tracker_id:   
# min_versions: []
# versions:     2.5.0
# qmid:         functional.dml.update_or_insert.update_or_insert_03

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TMPTEST_NOKEY ( id INTEGER , name VARCHAR(20));"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """UPDATE OR INSERT INTO TMPTEST_NOKEY(id, name) VALUES (1,'ivan' )
MATCHING (id);

select name from TMPTEST_NOKEY where id =1;

UPDATE OR INSERT INTO TMPTEST_NOKEY(id, name) VALUES (1,'bob' )
MATCHING (id);

select name from TMPTEST_NOKEY where id =1;

UPDATE OR INSERT INTO TMPTEST_NOKEY(id, name) VALUES (1,'ivan' );"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
NAME
====================
ivan


NAME
====================
bob

"""
expected_stderr_1 = """Statement failed, SQLSTATE = 22000
Dynamic SQL Error
-Primary key required on table TMPTEST_NOKEY
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

