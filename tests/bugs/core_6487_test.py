#coding:utf-8

"""
ID:          issue-6717
ISSUE:       6717
TITLE:       FETCH ABSOLUTE and RELATIVE beyond bounds of cursor should always position immediately before-first or after-last
DESCRIPTION:
JIRA:        CORE-6487
FBTEST:      bugs.core_6487
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set heading off;
    set term ^;
    execute block returns(id int, rc int) as
        declare c scroll cursor for
        (
            select  1 id from rdb$database union all
            select  2 id from rdb$database union all
            select  3 id from rdb$database
        )
        ;
    begin
        open c;
        fetch absolute 9223372036854775807 from c;

        fetch relative -(9223372036854775807-2) from c;
        id = c.id;
        rc = row_count;
        suspend;

        close c;
    end
    ^

    execute block returns(id int, rc int) as
        declare c scroll cursor for
        (
            select  1 id from rdb$database union all
            select  2 id from rdb$database union all
            select  3 id from rdb$database
        )
        ;
    begin
        open c;
        fetch absolute -9223372036854775808 from c;

        fetch relative (9223372036854775806) from c;
        id = c.id;
        rc = row_count;
        suspend;

        close c;
    end
    ^
    set term ;^
"""

act = isql_act('db', test_script, substitutions=[('-At block line:.*', '-At block line')])

expected_stderr = """
    Statement failed, SQLSTATE = HY109
    Cursor C is not positioned in a valid record
    -At block line: 14, col: 5

    Statement failed, SQLSTATE = HY109
    Cursor C is not positioned in a valid record
    -At block line: 14, col: 5
"""

@pytest.mark.version('>=3.0.8')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
