#coding:utf-8
#
# id:           bugs.core_1167
# title:        CHARACTER SET GBK is not installed
# decription:   Default character set is GBK
#               Create Table T1(ID integer, FName Varchar(20); -- OK
#               Commit; ---Error Message: CHARACTER SET GBK is not installed
# tracker_id:   CORE-1167
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1167

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='GBK', sql_dialect=3, init=init_script_1)

test_script_1 = """Create Table T1(ID integer, FName Varchar(20) CHARACTER SET GBK);
COMMIT;
SHOW TABLE T1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """ID                              INTEGER Nullable
FNAME                           VARCHAR(20) Nullable
"""

@pytest.mark.version('>=2.1')
def test_core_1167_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

