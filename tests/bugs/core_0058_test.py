#coding:utf-8
#
# id:           bugs.core_0058
# title:        WHERE CURRENT OF doesn't work
# decription:
# tracker_id:   CORE-0058
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('line: [0-9]+, col: [0-9]+', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22000
    no current record for fetch operation
    -At procedure 'TEST_UPD'
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

