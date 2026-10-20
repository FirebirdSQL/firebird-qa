#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9220
TITLE:       Profiler reports wrong or missing PSQL line statistics
DESCRIPTION:
NOTES:
    [20.10.2026] pzotov
    Confirmed bug on 6.0.0.2389-6b5f150.
    Checked on 6.0.0.2405-e71116c.
"""

import pytest
from firebird.qa import *

db = db_factory()
test_script = """
    set bail on;
    set list on;
    create table test (id integer);
    commit;
    insert into test select row_number()over() from rdb$types rows 5;
    commit;

    select rdb$profiler.start_session('test') as start_session from rdb$database;

    set term ^;
    execute block as
        declare n integer = 0;
    begin
        for select id from test into :n do
            n = n + 1;
    end
    ^
    execute block as
        declare n integer = 0;
    begin
        insert into test values (100);
        update or insert into test values (101) matching (id);
        for
            execute statement 'select id from test'
            into :n
        do
            n = n + 1;
        when any do
            n = 0;
    end
    ^
    set term ;^

    execute procedure rdb$profiler.finish_session(true);
    commit;
    set count on;
    select statement_id, line_num, column_num, counter
    from plg$profiler.plg$prof_psql_stats_view
    order by statement_id, line_num, column_num
    ;

"""

substitutions = [
    ('[ \t]+', ' ')
    ,('START_SESSION.*', '')
    ,('STATEMENT_ID\\s+\\d+', 'STATEMENT_ID')
    ,('LINE_NUM\\s+\\d+', 'LINE_NUM')
    ,('COLUMN_NUM\\s+\\d+', 'COLUMN_NUM')
]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    STATEMENT_ID                    6872
    LINE_NUM                        2
    COLUMN_NUM                      5
    COUNTER                         1

    STATEMENT_ID                    6872
    LINE_NUM                        4
    COLUMN_NUM                      5
    COUNTER                         6

    STATEMENT_ID                    6872
    LINE_NUM                        5
    COLUMN_NUM                      9
    COUNTER                         5

    STATEMENT_ID                    6881
    LINE_NUM                        2
    COLUMN_NUM                      5
    COUNTER                         1

    STATEMENT_ID                    6881
    LINE_NUM                        3
    COLUMN_NUM                      1
    COUNTER                         1

    STATEMENT_ID                    6881
    LINE_NUM                        4
    COLUMN_NUM                      5
    COUNTER                         1

    STATEMENT_ID                    6881
    LINE_NUM                        5
    COLUMN_NUM                      5
    COUNTER                         1

    STATEMENT_ID                    6881
    LINE_NUM                        6
    COLUMN_NUM                      5
    COUNTER                         8

    STATEMENT_ID                    6881
    LINE_NUM                        10
    COLUMN_NUM                      9
    COUNTER                         7

    Records affected: 9
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
