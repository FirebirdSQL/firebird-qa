#coding:utf-8
#
# id:           bugs.core_1227
# title:        LIST() function seems not work if used twice or more in a query
# decription:   f I try to use the LIST() function twice or more in a query the following error occurs:
#               
#               Undefined name.
#               Dynamic SQL Error.
#               SQL error code = -204.
#               Implementation limit exceeded.
#               Block size exceeds implementation restriction.
# tracker_id:   CORE-1227
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_1227

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TESTTABLE (ID integer, FIELD1 char(5), FIELD2 char(20));
INSERT INTO TESTTABLE VALUES (1,'aaaaa','bbbbbbbbb');
INSERT INTO TESTTABLE VALUES (1,'ccccc','ddddddddd');
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT LIST(FIELD1), LIST(FIELD2) FROM TESTTABLE GROUP BY ID;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """             LIST              LIST
================= =================
              0:1               0:2
==============================================================================
LIST:
aaaaa,ccccc
==============================================================================
==============================================================================
LIST:
bbbbbbbbb           ,ddddddddd
==============================================================================

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

