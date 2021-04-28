#coding:utf-8
#
# id:           bugs.core_1551
# title:        AV when all statements are cancelled
# decription:   
# tracker_id:   CORE-1551
# min_versions: []
# versions:     2.5.0
# qmid:         bugs.core_1551-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """delete from MON$STATEMENTS;
delete from MON$ATTACHMENTS;
COMMIT;
SELECT 1 FROM RDB$DATABASE;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CONSTANT
============
           1

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

