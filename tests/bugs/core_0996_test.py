#coding:utf-8
#
# id:           bugs.core_0996
# title:        Keyword AS not recognized in clause FROM
# decription:   The sentence SELECT * FROM <table> AS <alias> is not recognized correct.
# tracker_id:   CORE-996
# min_versions: []
# versions:     2.0
# qmid:         bugs.core_996

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE T1 (ID1 INTEGER NOT NULL);
INSERT INTO T1 VALUES (1);
COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT ID1 from T1 AS BLA;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """         ID1
============
           1
"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

