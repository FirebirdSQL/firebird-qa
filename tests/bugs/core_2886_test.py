#coding:utf-8
#
# id:           bugs.core_2886
# title:        Query with "NOT IN <subselect from view>" fails
# decription:   
# tracker_id:   CORE-2886
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE T (ID INTEGER NOT NULL);

CREATE VIEW V( ID) AS select ID from T;

INSERT INTO T (ID) VALUES (1);
INSERT INTO T (ID) VALUES (2);
INSERT INTO T (ID) VALUES (3);

COMMIT;
"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT ID FROM T
WHERE ID NOT IN
  (SELECT ID FROM V WHERE ID = 1);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          ID
============
           2
           3

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

