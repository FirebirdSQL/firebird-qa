#coding:utf-8
#
# id:           bugs.core_1253
# title:        LIST(DISTINCT) concatenate VARCHAR values as CHAR
# decription:   
# tracker_id:   CORE-1253
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1253

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE T1 (C1 varchar(5));
COMMIT;
INSERT INTO T1 VALUES ('1');
INSERT INTO T1 VALUES ('2');
COMMIT;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select list(distinct c1) from t1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """LIST
=================
              0:1
==============================================================================
LIST:
1,2
==============================================================================

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

