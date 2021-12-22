#coding:utf-8
#
# id:           bugs.core_4070
# title:        NOT-NULL-column can be used as primary key and filled with NULL-values
# decription:   
# tracker_id:   CORE-4070
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test01(uid char(16) character set octets collate octets);
    alter table test01 add constraint test01_pk primary key (uid);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER TABLE TEST01 failed
    -Column: UID not defined as NOT NULL - cannot be used in PRIMARY KEY constraint definition
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

