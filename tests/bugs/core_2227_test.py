#coding:utf-8

"""
ID:          issue-2655
ISSUE:       2655
TITLE:       Problem with column names with Accents and triggers
DESCRIPTION:
NOTES:
[25.1.2022] pcisar
  For yet unknown reason, ISQL gets malformed stdin from act.execute() although it was passed
  correctly encoded in iso8859_1. Test changed to use script file writen in iso8859_1
  which works fine.
JIRA:        CORE-2227
"""

import pytest
from pathlib import Path
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
    END
    ^
"""

act = isql_act('db', test_script)

script_file = temp_file('test_script.sql')

@pytest.mark.version('>=3')
def test_1(act: Action, script_file: Path):
    script_file.write_text(test_script, encoding='iso8859_1')
    act.isql(switches=[], input_file=script_file)
