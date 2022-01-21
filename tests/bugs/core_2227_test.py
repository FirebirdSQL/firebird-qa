#coding:utf-8

"""
ID:          issue-2655
ISSUE:       2655
TITLE:       Problem with column names with Accents and triggers
DESCRIPTION:
JIRA:        CORE-2227
"""

import pytest
from firebird.qa import *

init_script = """
   RECREATE TABLE TESTING (
      "CÓDIGO" INTEGER
  );
"""

db = db_factory(charset='ISO8859_1', init=init_script)

test_script = """
    SET TERM ^;
    CREATE TRIGGER TESTING_I FOR TESTING
    ACTIVE BEFORE INSERT POSITION 0
    AS
    BEGIN
      NEW."CÓDIGO" = 1;
    END ^
"""

act = isql_act('db', test_script)

@pytest.mark.version('>=3')
def test_1(act: Action):
    try:
        act.execute(charset='utf8')
    except ExecutionError as e:
        pytest.fail("Test script execution failed", pytrace=False)
