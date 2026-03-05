#coding:utf-8

"""
ID:          issue-3860
ISSUE:       3860
TITLE:       DROP VIEW ignores the existing non-column dependencies
DESCRIPTION:
JIRA:        CORE-3502
FBTEST:      bugs.core_3502
NOTES:
    [05.03.2026] pzotov
    Removed old substitutions.
    Adjusted expected output which has changed since #b38046e1 ('Encapsulation of metadata cache'; 24-feb-2026 17:31:04 +0000).
    Checked on 6.0.0.1807-46797ab; 5.0.4.1780-2040071; 4.0.7.3245; 3.0.14.33838
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
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

    execute procedure p;
    commit;

    drop view v;
"""

act = isql_act('db', test_script)

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    expected_stdout_5x = """
        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -cannot delete
        -COLUMN V.ID
        -there are 1 dependencies
    """
    expected_stdout_6x = """
        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -cannot delete
        -VIEW "PUBLIC"."V"
        -there are 1 dependencies
    """
    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
