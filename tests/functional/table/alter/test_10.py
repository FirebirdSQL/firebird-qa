#coding:utf-8

"""
ID:          table.alter-10
TITLE:       ALTER TABLE - DROP CONSTRAINT - PRIMARY KEY
DESCRIPTION:
FBTEST:      functional.table.alter.10
NOTES:
    [06.10.2023] pzotov
    Removed SHOW command. It is enough to check that we can add duplicate values in the table w/o PK.
"""

import pytest
from firebird.qa import *

db = db_factory(charset = 'utf8')

test_script = """
    set bail on;
    set list on;
    create table test(id int, constraint test_pk primary key(id));
    alter table test drop constraint test_pk;
    commit;
    insert into test(id) values(1);
    insert into test(id) values(1);
    commit;
    -- this must show two records with the same value:
    select * from test;
    commit;

    -- thist must FAIL because NOT NULL still active for ID:
    insert into test(id) values(null);
"""

act = isql_act('db', test_script)

expected_stdout = """
    ID                              1
    ID                              1
    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."ID", value "*** null ***"
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
