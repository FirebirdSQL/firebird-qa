#coding:utf-8
#
# id:           functional.dml.merge.01
# title:        Merge
# decription:   
# tracker_id:   CORE-815
# min_versions: []
# versions:     2.1
# qmid:         functional.dml.merge.merge_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE T1 (ID integer, NAME char(10), PRIMARY KEY(id));
CREATE TABLE T2 ( ID integer, NAME char(10), PRIMARY KEY(id));
COMMIT;
INSERT INTO T1 (ID,NAME) VALUES (1,'1NOMT1');
INSERT INTO T1 (ID,NAME) VALUES (2,'2NOMT1');
INSERT INTO T2 (ID,NAME) VALUES (1,'1NOMT2');
INSERT INTO T2 (ID,NAME) VALUES (2,'2NOMT2');
INSERT INTO T2 (ID,NAME) VALUES (3,'3NOMT2');
COMMIT;

"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """MERGE
 INTO T1
 USING (SELECT * FROM T2 WHERE id > 1) cd
	ON (T1.id = cd.id)
	WHEN MATCHED THEN
	UPDATE SET
	 name = cd.name
	WHEN NOT MATCHED THEN
	INSERT (id, name)
	 VALUES (cd.id, cd.name);
COMMIT;
SELECT ID, NAME FROM T1;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          ID NAME
============ ==========
           1 1NOMT1
           2 2NOMT2
           3 3NOMT2

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

