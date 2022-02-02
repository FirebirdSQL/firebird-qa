#coding:utf-8

"""
ID:          issue-4260
ISSUE:       4260
TITLE:       Creating self-referential FK crashes database (bug-check) whether constraint violation had place
DESCRIPTION:
  Confirmed on WI-V3.0.5.33118, WI-T4.0.0.1496: "SQLSTATE = 08006 / Error reading..." on last DELETE statement
  Checked on WI-V3.0.5.33123, WI-T4.0.0.1501 (both SS an CS): works OK, got only SQLSTATE = 23000 when try to add FK.
  DELETE statement does not raise error.
JIRA:        CORE-3925
FBTEST:      bugs.core_3925
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create table test(key integer not null primary key, ref integer);
    insert into test(key,ref) values(1,-1);
    commit;
    alter table test add constraint fk_key_ref foreign key (ref) references test(key);
    delete from test;
    commit;
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 23000
    violation of FOREIGN KEY constraint "FK_KEY_REF" on table "TEST"
    -Foreign key reference target does not exist
    -Problematic key value is ("REF" = -1)
"""

@pytest.mark.version('>=3.0.5')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

