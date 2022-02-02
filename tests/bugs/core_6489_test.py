#coding:utf-8

"""
ID:          issue-6719
ISSUE:       6719
TITLE:       User without ALTER ANY ROLE privilege can use COMMENT ON ROLE
DESCRIPTION:
JIRA:        CORE-6489
FBTEST:      bugs.core_6489
"""

import pytest
from firebird.qa import *

db = db_factory()

user_jr = user_factory('db', name='tmp$c6489_junior', password='123', plugin='Srp')
user_sr = user_factory('db', name='tmp$c6489_senior', password='456', plugin='Srp')

test_script = """
    grant alter any role to user tmp$c6489_senior;
    commit;

    connect '$(DSN)' user tmp$c6489_junior password '123';
    comment on role rdb$admin is 'Comment by tmp$c6489_junior';
    commit;

    connect '$(DSN)' user tmp$c6489_senior password '456';
    comment on role rdb$admin is 'Comment by tmp$c6489_senior';
    commit;

    set list on;
    select r.rdb$description as role_descr_blob_id from rdb$roles r where r.rdb$role_name = upper('rdb$admin');
    commit;

    comment on role rdb$admin is null;
    commit;
"""

act = isql_act('db', test_script,
               substitutions=[('ROLE_DESCR_BLOB_ID .*', ''), ('[\t ]+', ' '),
                              ('(-)?Effective user is.*', '')])

expected_stdout = """
    Comment by tmp$c6489_senior
"""

expected_stderr = """
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -COMMENT ON RDB$ADMIN failed
    -no permission for ALTER access to ROLE RDB$ADMIN
    -Effective user is TMP$C6489_JUNIOR
"""

@pytest.mark.version('>=3.0.8')
def test_1(act: Action, user_sr, user_jr):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
