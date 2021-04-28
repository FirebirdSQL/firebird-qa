#coding:utf-8
#
# id:           bugs.core_0925
# title:        ALL predicate works incorrectly for some subqueries
# decription:   
# tracker_id:   CORE-925
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_925

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE STAFF (EMPNUM CHAR(3) NOT NULL UNIQUE,
                     EMPNAME CHAR(20),
                     GRADE DECIMAL(4),
                     CITY CHAR(15));
 CREATE TABLE WORKS ( EMPNUM CHAR(3) NOT NULL,
                      PNUM CHAR(3) NOT NULL,
                      HOURS DECIMAL(5),
                      UNIQUE(EMPNUM,PNUM));
 COMMIT;

 INSERT INTO STAFF VALUES ('E1','Alice',12,'Deale');
 INSERT INTO STAFF VALUES ('E2','Betty',10,'Vienna');
 INSERT INTO STAFF VALUES ('E3','Carmen',13,'Vienna');
 INSERT INTO STAFF VALUES ('E4','Don',12,'Deale');
 INSERT INTO STAFF VALUES ('E5','Ed',13,'Akron');

 INSERT INTO WORKS VALUES ('E1','P1',40);
 INSERT INTO WORKS VALUES ('E1','P2',20);
 INSERT INTO WORKS VALUES ('E1','P3',80);
 INSERT INTO WORKS VALUES ('E1','P4',20);
 INSERT INTO WORKS VALUES ('E1','P5',12);
 INSERT INTO WORKS VALUES ('E1','P6',12);
 INSERT INTO WORKS VALUES ('E2','P1',40);
 INSERT INTO WORKS VALUES ('E2','P2',80);
 INSERT INTO WORKS VALUES ('E3','P2',20);
 INSERT INTO WORKS VALUES ('E4','P2',20);
 INSERT INTO WORKS VALUES ('E4','P4',40);
 INSERT INTO WORKS VALUES ('E4','P5',80);
 COMMIT;
"""

db_1 = db_factory(charset='ISO8859_1', sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT EMPNUM
FROM WORKS
GROUP BY EMPNUM
HAVING EMPNUM = ALL
  ( SELECT WORKS.EMPNUM
    FROM WORKS JOIN STAFF ON WORKS.EMPNUM = STAFF.EMPNUM );


"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.execute()

