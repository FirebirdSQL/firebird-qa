#coding:utf-8

"""
ID:          issue-2847
ISSUE:       2847
TITLE:       String values in error messages are not converted to connection charset
DESCRIPTION:
JIRA:        CORE-2431
"""

import pytest
from firebird.qa import *

db = db_factory(from_backup='core2431.fbk')

test_script = """
    set list on;
    select c.rdb$character_set_name as connection_cset
    from mon$attachments a
    join rdb$character_sets c on a.mon$character_set_id = c.rdb$character_set_id
    where a.mon$attachment_id = current_connection;

    set term ^;
    execute block as
    begin
      exception ex_bad_remainder using (-8);
    end
    ^
    set term ;^
    commit;
"""

act = isql_act('db', test_script,
                 substitutions=[('-At block line: [\\d]+, col: [\\d]+', '-At block line')])

expected_stdout = """
    CONNECTION_CSET                 WIN1251
"""

expected_stderr = """
    Statement failed, SQLSTATE = HY000
    exception 1
    -EX_BAD_REMAINDER
    -Новый остаток изделия будет отрицательным: -8
    -At block line: 3, col: 7
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute(charset='win1251')
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

