#coding:utf-8

"""
ID:          gtcs.minimum-grant
TITLE:       Minimum grant test
DESCRIPTION:
  ::: NB :::
  ### Name of original test has no any relation with actual task of this test: ###
  https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_34.script
FBTEST:      functional.gtcs.minimum_grant_test
"""

import pytest
from firebird.qa import *

substitutions = [('no permission for (read/select|SELECT) access.*', 'no permission for read access'),
                 ('no permission for (insert/write|INSERT) access.*', 'no permission for write access'),
                 ('[ \t]+', ' '), ('-{0,1}[ ]{0,1}Effective user is.*', '')]

db = db_factory()

test_script = """
    set list on;

    set term ^;
    execute block as
    begin
        begin
            execute statement 'drop user tmp$qa_user1' with autonomous transaction;
            when any do begin end
        end

        begin
            execute statement 'drop user tmp$qa_user2' with autonomous transaction;
            when any do begin end
        end

    end^
    set term ;^
    commit;

    create user tmp$qa_user1 password '123';
    create user tmp$qa_user2 password '456';
    commit;

    create table test (c1 int);
    commit;

    grant insert on test to tmp$qa_user1;
    grant select on test to tmp$qa_user2;
    commit;

    -------------------------------------------------
    connect '$(DSN)' user tmp$qa_user1 password '123';
    select current_user as whoami from rdb$database;
    insert into test values(1); -- should pass
    select * from test;    -- should fail
    commit;

    -------------------------------------------------
    connect '$(DSN)' user tmp$qa_user2 password '456';
    select current_user as whoami from rdb$database;
    insert into test values(2);    -- should fail
    select * from test; -- should pass
    commit;
"""

act = isql_act('db', test_script, substitutions=substitutions)

expected_stdout = """
    WHOAMI                          TMP$QA_USER1
    WHOAMI                          TMP$QA_USER2
    C1                              1
"""

expected_stderr = """
    Statement failed, SQLSTATE = 28000
    no permission for read/select access to TABLE TEST

    Statement failed, SQLSTATE = 28000
    no permission for insert/write access to TABLE TEST
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
