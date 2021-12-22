#coding:utf-8
#
# id:           bugs.core_5707
# title:        Begin and end of physical backup in the same transaction could crash engine
# decription:   
#                   Confirmed crashes on:
#                       3.0.3.32837
#                       4.0.0.800
#                   Could NOT reproduce on 3.0.3.32882 (SS).
#                   Checked on:
#                       30SS, build 3.0.3.32887: OK, 0.844s.
#                       40SS, build 4.0.0.861: OK, 2.016s.
#                
# tracker_id:   CORE-5707
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    alter database begin backup end backup;
    commit;
    set autoddl off;
    alter database begin backup;
    alter database end backup;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER DATABASE failed
    -Incompatible ALTER DATABASE clauses: 'BEGIN BACKUP' and 'END BACKUP'
"""

@pytest.mark.version('>=3.0.3')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

