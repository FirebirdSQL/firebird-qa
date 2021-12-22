#coding:utf-8
#
# id:           bugs.core_3211
# title:        String truncation occurs when selecting from a view containing NOT IN inside
# decription:   
# tracker_id:   CORE-3211
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE T ( ID integer, FIELD1 varchar(30) );
COMMIT;
CREATE VIEW VT ( ID )
AS
  select T1.ID from T as T1 where T1.FIELD1 not in ( select T2.FIELD1 from T as T2 where T2.FIELD1 = 'system1' )
;
COMMIT;
INSERT INTO T (ID, FIELD1) VALUES (1, 'system');
INSERT INTO T (ID, FIELD1) VALUES (2, 'system');
INSERT INTO T (ID, FIELD1) VALUES (3, 'system');
INSERT INTO T (ID, FIELD1) VALUES (4, 'system');
INSERT INTO T (ID, FIELD1) VALUES (5, 'system');
COMMIT;"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select * from VT;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\Users\\win7\\Firebird_tests\\fbt-repository\\tmp\\bugs.core_3211.fdb, User: SYSDBA
SQL>
          ID
============
           1
           2
           3
           4
           5

SQL>"""

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

