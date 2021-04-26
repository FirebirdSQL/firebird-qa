#coding:utf-8
#
# id:           functional.view.create.10
# title:        CREATE VIEW as SELECT ....
# decription:   Create view without field list
# tracker_id:   CORE-831
# min_versions: []
# versions:     2.1
# qmid:         functional.view.create.create_view_10

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE T1 (ID INTEGER, NAME VARCHAR(10));
COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE VIEW V1 AS SELECT ID AS VID, NAME FROM T1;
COMMIT;
SHOW VIEW V1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """VID                             INTEGER Nullable
NAME                            VARCHAR(10) Nullable
View Source:
==== ======
 SELECT ID AS VID, NAME FROM T1
"""

@pytest.mark.version('>=2.1')
def test_10_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

