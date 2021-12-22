#coding:utf-8
#
# id:           bugs.core_1810
# title:        Usernames with '.' character
# decription:
# tracker_id:   CORE-1810
# min_versions: ['2.1.7']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('Statement failed, SQLSTATE.*', ''), ('record not found for user:.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set wng off;
    recreate table test(id int, x int, y int, z int);
    commit;
    insert into test values(1, 100, 200, 300);
    commit;
    drop user "$.$";
    commit;
    create role "#.#";
    commit;
    create user "$.$" password '123';
    commit;

    revoke all on all from "$.$";
    grant "#.#" to "$.$";
    grant select on test to "#.#";
    commit;

    connect '$(DSN)' user "$.$" password '123' role "#.#";
    commit;

    select
        current_user,
        current_role,
        iif( upper(a.mon$remote_protocol) starting with upper('TCP'), 'YES', 'NO!') is_remote_connection
    from rdb$database m
    join mon$attachments a on a.mon$attachment_id = current_connection
    ;

    select * from test;
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    commit;
    drop user "$.$";
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    USER                            $.$
    ROLE                            #.#
    IS_REMOTE_CONNECTION            YES

    ID                              1
    X                               100
    Y                               200
    Z                               300
"""

expected_stderr_1 = """
    Statement failed, SQLSTATE = HY000
    record not found for user: $.$
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
    assert act_1.clean_stderr == act_1.clean_expected_stderr

