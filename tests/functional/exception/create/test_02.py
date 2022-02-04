#coding:utf-8

"""
ID:          exception.create-02
FBTEST:      functional.exception.create.02
TITLE:       CREATE EXCEPTION - try create Exception with the same name
DESCRIPTION:
"""

import pytest
from firebird.qa import *

init_script = """CREATE EXCEPTION test 'A1';
commit;"""

db = db_factory(sql_dialect=3, init=init_script)

act = isql_act('db', "CREATE EXCEPTION test 'message to show';")

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE EXCEPTION TEST failed
-Exception TEST already exists
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
