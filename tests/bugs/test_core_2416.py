#coding:utf-8
#
# id:           bugs.core_2416
# title:        AV preparing a query with aggregate over derived table
# decription:   
# tracker_id:   CORE-2416
# min_versions: []
# versions:     2.1.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """WITH
  t0 AS (
    SELECT 1 AS f0, date '01.03.09' AS f1, 'Event1' AS f2
      FROM rdb$database
  ),

  t1 (f1) AS (
    SELECT MIN(t2.f1) AS f1 FROM t0 AS t2 WHERE t2.f0 > t3.f0 AND t2.f1 >= t3.f1 AND t2.f2 = t3.f2
  )

SELECT t4.f2, t4.f1_p
  FROM (SELECT t3.f0, t3.f1, t3.f2, CAST((SELECT t1.f1 FROM t1) - t3.f1 AS INTEGER) AS f1_p
          FROM t0 AS t3
       ) AS t4
  WHERE t4.f1_p IS NOT NULL
GROUP BY t4.f2, t4.f1_p;

SELECT t4.f2, t4.f1_p
  FROM (SELECT t3.f0, t3.f1, t3.f2,
               CAST((SELECT t1.f1 FROM (
                            SELECT MIN(t2.f1) AS f1 FROM (
                                   SELECT 1 AS f0, date '01.03.09' AS f1, 'Event1' AS f2
                                     FROM rdb$database) AS t2
                             WHERE t2.f0 > t3.f0 AND t2.f1 >= t3.f1 AND t2.f2 = t3.f2) as t1)
                    - t3.f1 AS INTEGER) AS f1_p
          FROM (
            SELECT 1 AS f0, date '01.03.09' AS f1, 'Event1' AS f2
              FROM rdb$database) AS t3
       ) AS t4
  WHERE t4.f1_p IS NOT NULL
GROUP BY t4.f2, t4.f1_p ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1.3')
def test_core_2416_1(act_1: Action):
    act_1.execute()

