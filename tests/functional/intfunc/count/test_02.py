#coding:utf-8

"""
ID:          intfunc.count-02
TITLE:       COUNT
DESCRIPTION: Count of Not Null values and count of rows and count of distinct values
FBTEST:      functional.intfunc.count.02
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE test( id INTEGER);
INSERT INTO test VALUES(0);
INSERT INTO test VALUES(0);
INSERT INTO test VALUES(null);
INSERT INTO test VALUES(null);
INSERT INTO test VALUES(null);
INSERT INTO test VALUES(1);
INSERT INTO test VALUES(1);
INSERT INTO test VALUES(1);
INSERT INTO test VALUES(1);
"""

db = db_factory(init=init_script)

act = isql_act('db', "SELECT COUNT(*), COUNT(ID), COUNT(DISTINCT ID) FROM test;")

expected_stdout = """                COUNT                 COUNT                 COUNT
===================== ===================== =====================
                    9                     6                     2
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
