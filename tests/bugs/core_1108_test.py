#coding:utf-8
#
# id:           bugs.core_1108
# title:        Wrong results with GROUP BY on constants
# decription:   This test may hang (or take very long time to finish) the server version 1.5.x
# tracker_id:   CORE-1108
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_1108-21

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE EMPLOYEE (
    EMP_NO SMALLINT,
    JOB_COUNTRY VARCHAR(15));

COMMIT;

INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (2, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (4, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (5, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (8, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (9, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (11, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (12, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (14, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (15, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (20, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (24, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (28, 'England');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (29, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (34, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (36, 'England');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (37, 'England');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (44, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (45, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (46, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (52, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (61, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (65, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (71, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (72, 'Canada');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (83, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (85, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (94, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (105, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (107, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (109, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (110, 'Japan');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (113, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (114, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (118, 'Japan');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (121, 'Italy');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (127, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (134, 'France');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (136, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (138, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (141, 'Switzerland');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (144, 'USA');
INSERT INTO EMPLOYEE (EMP_NO, JOB_COUNTRY) VALUES (145, 'USA');

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """Select 'Country:', Job_Country, Count(*)
  From Employee
  Group By 1,2;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """CONSTANT JOB_COUNTRY                     COUNT
======== =============== =====================
Country: Canada                              1
Country: England                             3
Country: France                              1
Country: Italy                               1
Country: Japan                               2
Country: Switzerland                         1
Country: USA                                33

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

