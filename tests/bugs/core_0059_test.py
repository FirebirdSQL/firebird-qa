#coding:utf-8

"""
ID:          bugs.core_0059
ISSUE:       384
TITLE:       Automatic not null in PK columns incomplete
DESCRIPTION:
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test (a int, b float, c varchar(10), primary key (a, b, c));
    commit;
    insert into test(a) values(null);
    insert into test(a,b) values(1,null);
    insert into test(a,b,c) values(1,1,null);
    insert into test default values;
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."A", value "*** null ***"
    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."B", value "*** null ***"
    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."C", value "*** null ***"
    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."A", value "*** null ***"
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

