#coding:utf-8

"""
ID:          issue-5834
ISSUE:       5834
TITLE:       Direct system table modifications are not completely prohibited
DESCRIPTION:
JIRA:        CORE-5567
FBTEST:      bugs.core_5567
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    execute block as
    begin
      execute statement 'drop domain dm_test';
      when any do begin end
    end
    ^
    set term ;^
    commit;

    create domain dm_test numeric(18, 2);
    commit;

    set term ^;
    execute block as
        declare procedure hack as
        begin
            update rdb$fields set rdb$field_scale = -3 where rdb$field_name = upper('dm_test');
        end
    begin
        execute procedure hack;
    end
    ^
    set term ;^
    commit;

    set list on;
    select ff.rdb$field_scale domain_precision
    from rdb$fields ff
    where ff.rdb$field_name = upper('dm_test')
    ;

"""

act = isql_act('db', test_script, substitutions=[('line: [\\d]+, col: [\\d]+', ''), ('.*At block.*', '')])

expected_stdout = """
    DOMAIN_PRECISION                -2
"""

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    UPDATE operation is not allowed for system table RDB$FIELDS
    -At sub procedure 'HACK'
"""

@pytest.mark.version('>=3.0.3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

