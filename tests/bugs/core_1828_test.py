#coding:utf-8
#
# id:           bugs.core_1828
# title:        Error with ABS in dialect 1
# decription:   
# tracker_id:   CORE-1828
# min_versions: ['2.5']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TEST (MYNUM INTEGER);
COMMIT;
INSERT INTO TEST (MYNUM) VALUES (1);
INSERT INTO TEST (MYNUM) VALUES (-1);
INSERT INTO TEST (MYNUM) VALUES (2147483647);
INSERT INTO TEST (MYNUM) VALUES (-2147483648);
COMMIT;
"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=1, init=init_script_1)

test_script_1 = """SELECT ABS(MYNUM) FROM TEST;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                    ABS
=======================
      1.000000000000000
      1.000000000000000
      2147483647.000000
      2147483648.000000

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

