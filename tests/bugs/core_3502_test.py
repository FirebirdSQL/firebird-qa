#coding:utf-8

"""
ID:          issue-3860
ISSUE:       3860
TITLE:       DROP VIEW ignores the existing non-column dependencies
DESCRIPTION:
JIRA:        CORE-3502
"""

import pytest
from firebird.qa import *

init_script = """
    set autoddl on;
    commit;
    create or alter procedure p as begin end;
    commit;

    create or alter view v (id) as select rdb$relation_id from rdb$database;
    commit;

    set term ^;
    create or alter procedure p as
      declare id int;
    begin
      select id from v rows 1 into id;
    end^
    set term ;^
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    execute procedure p;
    commit;
    drop view v;
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN V.ID
    -there are 1 dependencies
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

