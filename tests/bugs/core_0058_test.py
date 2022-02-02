#coding:utf-8

"""
ID:          issue-383
ISSUE:       383
TITLE:       WHERE CURRENT OF doesn't work
DESCRIPTION:
JIRA:        CORE-58
FBTEST:      bugs.core_0058
"""

import pytest
from firebird.qa import *

substitutions = [('line: [0-9]+, col: [0-9]+', '')]

db = db_factory()

test_script = """
    -- NB: changed expected value of SQLSTATE to actual. See comment in git:
    -- "Prevent stack trace (line/column info) from overriding the real error's SQLSTATE", 30-apr-2016
    -- https://github.com/FirebirdSQL/firebird/commit/d1d8b36a07d4f11d98d2c8ec16fb8ec073da442b // FB 4.0
    -- https://github.com/FirebirdSQL/firebird/commit/849bfac745bc9158e9ef7990f5d52913f8b72f02 // FB 3.0
    -- https://github.com/FirebirdSQL/firebird/commit/b9d4142c4ed1fdf9b7c633edc7b2425f7b93eed0 // FB 2.5
    -- See also letter from dimitr, 03-may-2016 19:24.

    recreate table test (a integer not null, constraint test_pk primary key (a));
    insert into test (a) values (1);
    insert into test (a) values (2);
    insert into test (a) values (3);
    insert into test (a) values (4);
    commit;

    set term ^;
    create procedure test_upd(d integer) as
        declare c cursor for (
            select a from test
        );
    begin
        open c;
        update test set a = a + :d
        where current of c;
        close c;
    end
    ^
    set term ;^
    commit;

    execute procedure test_upd (2);
"""

act = isql_act('db', test_script, substitutions=substitutions)

expected_stderr = """
    Statement failed, SQLSTATE = 22000
    no current record for fetch operation
    -At procedure 'TEST_UPD'
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

