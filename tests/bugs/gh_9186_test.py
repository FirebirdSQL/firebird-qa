#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9186
TITLE:       LIKE, CONTAINING, STARTING WITH and SIMILAR TO fail on DATE/TIME/TIMESTAMP and approximate numeric operands since gh_9108
DESCRIPTION:
NOTES:
    [05.10.2026] pzotov
    Confirmed bug on 6.0.0.2191-717c2a2.
    Checked on 6.0.0.2197-1e316df; 5.0.5.1895; 4.0.8.3327
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set bail on;
    recreate table test (
        dt date
        ,tm time 
        ,ts timestamp
        ,tmtz time with time zone
        ,tstz timestamp with time zone
        ,flt float
        ,dbl double precision
        ,df decfloat(16)
        ,i128 int128
    );
    insert into test values (
        date '2024-09-05'
        ,time '10:00:00'
        ,timestamp '2024-09-05 10:00:00'
        ,'10:00:00 Indian/Cocos'
        ,'2024-09-05 10:00:00 Indian/Cocos'
        ,3.5
        ,3.5
        ,3.5
        ,35
    );
    commit;

    set bail off;

    -- *** CHECK #1 ***
    -- Before fix, following statements raised `conversion error from string ...`.
    -- Expected: all of them shoudl return 1.
    select count(*) as cnt_1000 from test where dt like '2024%';
    select count(*) as cnt_1010 from test where dt containing '-09-';
    select count(*) as cnt_1020 from test where dt starting with '2024';
    select count(*) as cnt_1030 from test where dt similar to '2024%';

    select count(*) as cnt_2000 from test where tm like '10%';

    select count(*) as cnt_3000 from test where ts like '%10:00%';

    select count(*) as cnt_4000 from test where tmtz like '10%';         

    select count(*) as cnt_5000 from test where tstz like '%10:00%';     


    select count(*) as cnt_6000 from test where flt like '3%';           

    select count(*) as cnt_6500 from test where dbl like '3%';

    select count(*) as cnt_7000 from test where df like '3%';
    select count(*) as cnt_8000 from test where i128 like '3%';

    -- *** CHECK #2 ***
    -- When the pattern happens to be a valid literal of the operand type, the result silently changes instead.
    -- The pattern is converted to a date and then back to text in the default format:
    select count(*) as cnt_9100 from test where dt like '5-SEP-2024';     -- master: 1, 5.0: 0
    select count(*) as cnt_9200 from test where dt containing '5.9.2024'; -- master: 1, 5.0: 0

"""
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    CNT_1000 1
    CNT_1010 1
    CNT_1020 1
    CNT_1030 1
    CNT_2000 1
    CNT_3000 1
    CNT_4000 1
    CNT_5000 1
    CNT_6000 1
    CNT_6500 1
    CNT_7000 1
    CNT_8000 1
    CNT_9100 0
    CNT_9200 0
"""

@pytest.mark.version('>=4')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

