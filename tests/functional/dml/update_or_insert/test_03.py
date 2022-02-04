#coding:utf-8

"""
ID:          dml.update-or-insert-03
FBTEST:      functional.dml.update_or_insert.03
TITLE:       UPDATE OR INSERT
DESCRIPTION: MATCHING clause
"""

import pytest
from firebird.qa import *

db = db_factory(init="CREATE TABLE TMPTEST_NOKEY ( id INTEGER , name VARCHAR(20));")

test_script = """UPDATE OR INSERT INTO TMPTEST_NOKEY(id, name) VALUES (1,'ivan' )
MATCHING (id);

select name from TMPTEST_NOKEY where id =1;

UPDATE OR INSERT INTO TMPTEST_NOKEY(id, name) VALUES (1,'bob' )
MATCHING (id);

select name from TMPTEST_NOKEY where id =1;

UPDATE OR INSERT INTO TMPTEST_NOKEY(id, name) VALUES (1,'ivan' );"""

act = isql_act('db', test_script)

expected_stdout = """
NAME
====================
ivan


NAME
====================
bob
"""

expected_stderr = """Statement failed, SQLSTATE = 22000
Dynamic SQL Error
-Primary key required on table TMPTEST_NOKEY"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
