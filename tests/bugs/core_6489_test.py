#coding:utf-8
#
# id:           bugs.core_6489
# title:        User without ALTER ANY ROLE privilege can use COMMENT ON ROLE
# decription:   
#                  Test creates two users: one of them has no any rights, second is granted with 'alter any role' privilege.
#                  First user ('junior') must not have ability to add comment to rdb$admin role, but second ('senior') must
#                  be able to set comment to any string and make it null.
#               
#                  Confirmed bug on 4.0.0.2384, 3.0.8.33425
#                  Checked on: 4.0.0.2387, 3.0.8.33426 -- all OK.
#               
#                  NOTE:
#                  phrase '-Effective user is ...' presents only in FB 4.x and is suppressed here.
#                
# tracker_id:   CORE-6489
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = [('ROLE_DESCR_BLOB_ID .*', ''), ('[\t ]+', ' '), ('(-)?Effective user is.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter user tmp$c6489_junior password '123' using plugin Srp;
    create or alter user tmp$c6489_senior password '456' using plugin Srp;
    commit;
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
    
    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    drop user tmp$c6489_junior using plugin Srp;
    drop user tmp$c6489_senior using plugin Srp;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Comment by tmp$c6489_senior
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -COMMENT ON RDB$ADMIN failed
    -no permission for ALTER access to ROLE RDB$ADMIN
    -Effective user is TMP$C6489_JUNIOR
"""

@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

