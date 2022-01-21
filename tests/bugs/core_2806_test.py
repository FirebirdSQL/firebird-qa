#coding:utf-8

"""
ID:          issue-3194
ISSUE:       3194
TITLE:       Views based on procedures can't be created if the proc's output fields participate in an expression
DESCRIPTION:
JIRA:        CORE-2806
"""

import pytest
from firebird.qa import *

db = db_factory(charset='UTF8')

test_script = """set term ^;
create procedure p returns(rc int) as begin rc = 1; suspend; end^
create view v2(dosrc) as select rc * 2 from p^
commit ^
show view v2^
"""

act = isql_act('db', test_script)

expected_stdout = """DOSRC                           BIGINT Expression
View Source:
==== ======
 select rc * 2 from p
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

