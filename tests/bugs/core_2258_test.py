#coding:utf-8
#
# id:           bugs.core_2258
# title:        internal error when select upper(<blob>) from union
# decription:   
# tracker_id:   CORE-2258
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT * FROM
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
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

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

