#coding:utf-8

"""
ID:          issue-2684
ISSUE:       2684
TITLE:       Internal error when select upper(<blob>) from union
DESCRIPTION:
JIRA:        CORE-2258
FBTEST:      bugs.core_2258
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """SELECT * FROM
  (
   SELECT CAST('123' AS BLOB SUB_TYPE TEXT) FROM RDB$DATABASE
   UNION ALL
   SELECT CAST('123' AS BLOB SUB_TYPE TEXT) FROM RDB$DATABASE
   ) AS R (BLOB_FIELD)
;

SELECT UPPER(BLOB_FIELD) FROM
  (
   SELECT CAST('123' AS BLOB SUB_TYPE TEXT) FROM RDB$DATABASE
   UNION ALL
   SELECT CAST('123' AS BLOB SUB_TYPE TEXT) FROM RDB$DATABASE
   ) AS R (BLOB_FIELD)
;
"""

act = isql_act('db', test_script)

expected_stdout = """
       BLOB_FIELD
=================
              0:1
==============================================================================
BLOB_FIELD:
123
==============================================================================
              0:2
==============================================================================
BLOB_FIELD:
123
==============================================================================


            UPPER
=================
              0:7
==============================================================================
UPPER:
123
==============================================================================
              0:a
==============================================================================
UPPER:
123
==============================================================================

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

