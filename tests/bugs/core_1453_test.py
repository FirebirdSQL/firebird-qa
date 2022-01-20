#coding:utf-8

"""
ID:          issue-1871
ISSUE:       1871
TITLE:       Allow usage of functions in LIST delimiter parameter
DESCRIPTION:
JIRA:        CORE-1443
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE T1 (ID INTEGER, NAME CHAR(20));
COMMIT;
INSERT INTO T1 (ID,NAME) VALUES (1,'ORANGE');
INSERT INTO T1 (ID,NAME) VALUES (1,'APPLE');
INSERT INTO T1 (ID,NAME) VALUES (1,'LEMON');
INSERT INTO T1 (ID,NAME) VALUES (2,'ORANGE');
INSERT INTO T1 (ID,NAME) VALUES (2,'APPLE');
INSERT INTO T1 (ID,NAME) VALUES (2,'PEAR');
COMMIT;
"""

db = db_factory(init=init_script)

test_script = """select ID,  LIST( trim(NAME), ASCII_CHAR(35) )
from T1
group by 1;
"""

act = isql_act('db', test_script)

expected_stdout = """
          ID              LIST
============ =================
           1               0:1
==============================================================================
LIST:
ORANGE#LEMON#APPLE
==============================================================================
           2               0:2
==============================================================================
LIST:
PEAR#ORANGE#APPLE
==============================================================================

"""

@pytest.mark.version('>=2.5.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

