#coding:utf-8

"""
ID:          generator.create-02
FBTEST:      functional.generator.create.02
TITLE:       CREATE GENERATOR - try create gen with same name
DESCRIPTION:
"""
import pytest
from firebird.qa import *

init_script = """
    CREATE GENERATOR test;
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    CREATE GENERATOR test;
"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE SEQUENCE TEST failed
    -Sequence TEST already exists
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
