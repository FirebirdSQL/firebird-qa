#coding:utf-8

"""
ID:          issue-3681
ISSUE:       3681
TITLE:       Dependencies are not removed after dropping the procedure and the table it depends on in the same transaction
DESCRIPTION:
JIRA:        CORE-3314
"""

import pytest
from firebird.qa import *

init_script = """create table t (a int);
SET TERM !!;
create procedure p as begin delete from t; end!!
SET TERM !!;
commit;
"""

db = db_factory(init=init_script)

test_script = """SELECT 1 FROM  RDB$DEPENDENCIES WHERE RDB$DEPENDED_ON_NAME='T';
drop procedure p;
drop table t;
commit;
SELECT 1 FROM  RDB$DEPENDENCIES WHERE RDB$DEPENDED_ON_NAME='T';
"""

act = isql_act('db', test_script)

expected_stdout = """
    CONSTANT
============
           1
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

