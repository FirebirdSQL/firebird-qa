#coding:utf-8

"""
ID:          issue-517
ISSUE:       517
TITLE:       Trigger with except-s on view with union
DESCRIPTION:
JIRA:        CORE-190
FBTEST:      bugs.core_0190
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create table a (id integer);

    create view v1 (vid) as
    select id from a
    union all
    select id from a;

    create exception exa 'foo!..';
    create exception exb 'bar!..';
    commit;

    set term ^;
    create trigger tv1 for v1 active before update as
    begin
        if (new.vid = 0) then
            exception exa;
        else
            exception exb;
    end
    ^
    set term ;^
    commit;
"""

act = isql_act('db', test_script)

expected_stdout = """
"""

expected_stderr = """
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
    assert act.clean_stderr == act.clean_expected_stderr
