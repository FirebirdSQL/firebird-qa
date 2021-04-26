#coding:utf-8
#
# id:           bugs.core_3176
# title:        View with "subselect" column join table and not use index
# decription:   
# tracker_id:   CORE-3176
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TMP
(
  ID Integer NOT NULL,
  CONSTRAINT PK_TMP_1 PRIMARY KEY (ID)
);
COMMIT;
CREATE VIEW TMP_VIEW (ID1, ID2)
AS
SELECT 1,(SELECT 1 FROM RDB$DATABASE) FROM RDB$DATABASE;
COMMIT;"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT * FROM tmp_view TV LEFT JOIN tmp T ON T.id=TV.id2;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\Users\\win7\\Firebird_tests\\fbt-repository\\tmp\\bugs.core_3176.fdb, User: SYSDBA
SQL> SQL>
PLAN (TV RDB$DATABASE NATURAL)
PLAN (TV RDB$DATABASE NATURAL)
PLAN JOIN (TV RDB$DATABASE NATURAL, T INDEX (PK_TMP_1))

         ID1          ID2           ID
============ ============ ============
           1            1       <null>

SQL>"""

@pytest.mark.version('>=2.5.1')
def test_core_3176_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

