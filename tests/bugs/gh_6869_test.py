#coding:utf-8

"""
ID:          issue-6869
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/6869
TITLE:       Domain CHECK-expression can be ignored when we DROP objects that are involved in it
NOTES:
    [25.02.2023] pzotov
        Confirmed bug on 5.0.0.520.
        Checked on 5.0.0.959 - all OK.
    [23.06.2026] pzotov
        Adjusted output in 6.x to the actual one.
        Since #9247c82b ("Feature #8974 - Temporary Tables in Packages (#8983)") attempt to drop a TABLE
        that has dependent object(s) fails with text 'cannot delete _TABLE_ ...' rather than 'COLUMN ...'.
        (weird 'detalization' about dependency on table *COLUMN* exists in 3.x ... 5.x).
        Currently 6.x raise message with CORRECT text which does not mention any columns.
        Checked on 6.0.0.2023-8e2b38a.
"""

import pytest
from firebird.qa import *

init_script = """
    create domain dm_int as int;
    create table test(i dm_int);

    set term ^;
    create function fn_test(a_id dm_int) returns dm_int as
    begin
        return ( select min(i) from test );
    end
    ^
    set term ;^
    alter domain dm_int add constraint check ( value = (select fn_test(max(i)) from test) );
    commit;
"""
db = db_factory(init = init_script)

test_script = """
    set term ^;
    execute block as
    begin
        execute statement 'drop table test'; -- PASSED, despite having two dependent objects (function and domain expr.)
    end
    ^
    execute block as
    begin
        execute statement 'drop function fn_test'; -- PASSED, despite having dependent object (domain expr.)
    end
    ^
    set term ;^
    commit;
"""

act = isql_act('db', test_script)

expected_stdout_5x = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN TEST.I
    -there are 1 dependencies

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN TEST.I
    -there are 1 dependencies
"""

expected_stdout_6x = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -TABLE "PUBLIC"."TEST"
    -there are 1 dependencies
    
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -TABLE "PUBLIC"."TEST"
    -there are 1 dependencies
"""

@pytest.mark.version('>=5.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
