#coding:utf-8

"""
ID:          table.create-07
TITLE:       CREATE TABLE - unknown datatype (domain)
DESCRIPTION:
FBTEST:      functional.table.create.07
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE TABLE test(
 c1 unk_domain
);
"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE TABLE TEST failed
-SQL error code = -607
-Invalid command
-Specified domain or source column UNK_DOMAIN does not exist
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
