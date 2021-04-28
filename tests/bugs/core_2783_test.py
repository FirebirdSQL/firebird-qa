#coding:utf-8
#
# id:           bugs.core_2783
# title:        AV using recursive query as subquery in SELECT list and ORDER'ing by them
# decription:   
# tracker_id:   CORE-2783
# min_versions: []
# versions:     2.1.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT RDB$RELATION_ID,
       (WITH RECURSIVE
         NUM (ID) AS
         (
           SELECT 1 FROM RDB$DATABASE

           UNION ALL

           SELECT ID + 1
             FROM NUM
            WHERE ID < 10
         )
        SELECT MAX(ID) FROM NUM
       ) AS NNN
  FROM RDB$DATABASE
ORDER BY NNN;
WITH RECURSIVE
  NUM (ID) AS
  (
           SELECT 1 FROM RDB$DATABASE

           UNION ALL

           SELECT ID + 1
             FROM NUM
            WHERE ID < 10
  )
SELECT RDB$RELATION_ID, (SELECT MAX(ID) FROM NUM) AS NNN
  FROM RDB$DATABASE
ORDER BY NNN;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:btest2	mpugs.core_2783.fdb, User: SYSDBA
SQL> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON>
RDB$RELATION_ID          NNN
=============== ============
            128           10

SQL> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON>
RDB$RELATION_ID          NNN
=============== ============
            128           10

SQL>"""

@pytest.mark.version('>=2.1.4')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

