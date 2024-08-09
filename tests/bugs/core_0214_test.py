#coding:utf-8

"""
ID:          issue-542
ISSUE:       542
TITLE:       Count ( DISTINCT ... ) is too slow
DESCRIPTION:
    This test does following:
    1. Creates several tables with different number of unique values in field ID.
    2. Measures for each table time for two statements:
    2.1. select count(*) from ( select distinct id from ... )
    vs
    2.2. select count(distinct id) from ...
    3. If time for 2.1 exceeds time for 2.2 more than <X> times -  output message
       about possible regression. After multiple runs it was found that ratio for
       2.1 vs 2.2 is about 1.05 ... 1.10.  Constant <X> (threshold) was selected
       to be enough for not to be "violated".
JIRA:        CORE-214
FBTEST:      bugs.core_0214
"""

import pytest
from firebird.qa import *

db = db_factory()

MAX_DIFF = 3.0

test_script = f"""
    recreate table test1e1(id int); -- 10^1 distinct values
    recreate table test1e2(id int); -- 10^2 distinct values
    recreate table test1e3(id int); -- 10^3 distinct values
    recreate table test1e4(id int); -- 10^4 distinct values
    recreate table test1e5(id int); -- 10^5 distinct values
    commit;

    create or alter view v_fill as
    with recursive
    r as(select 0 i from rdb$database union all select r.i+1 from r where r.i<9)
    select r4.i * 10000 + r3.i * 1000 + r2.i * 100 + r1.i * 10 + r0.i as id
    from r r4, r r3, r r2, r r1, r r0;
    commit;

    insert into test1e1 select mod(id, 10) from v_fill;
    insert into test1e2 select mod(id, 100) from v_fill;
    insert into test1e3 select mod(id, 1000) from v_fill;
    insert into test1e4 select mod(id, 10000) from v_fill;
    insert into test1e5 select mod(id, 100000) from v_fill;
    commit;

    set list on;

    set term ^;

    execute block returns (
         ratio_for_1e1 varchar(150)
        ,ratio_for_1e2 varchar(150)
        ,ratio_for_1e3 varchar(150)
        ,ratio_for_1e4 varchar(150)
        ,ratio_for_1e5 varchar(150)
    )
    as
        -- ############################################
        -- ############    T H R E S H O L D   ########

        -- Before 28.10.2015: 1.85 (changed after letter by dimitr).
        -- Probably random disturbance was caused by other (concurrent) processes on test host.
        -- Check with new threshold was done on: WI-V2.5.5.26942 (SC) and WI-V3.0.0.32134 (CS/SC/SS).

        declare max_diff_threshold numeric(10,4) = {MAX_DIFF};

        -- ############################################

        declare ratio_select_vs_count_1e1 numeric(10,4);
        declare ratio_select_vs_count_1e2 numeric(10,4);
        declare ratio_select_vs_count_1e3 numeric(10,4);
        declare ratio_select_vs_count_1e4 numeric(10,4);
        declare ratio_select_vs_count_1e5 numeric(10,4);
        declare sel_distinct_1e1_ms int;
        declare cnt_distinct_1e1_ms int;
        declare sel_distinct_1e2_ms int;
        declare cnt_distinct_1e2_ms int;
        declare sel_distinct_1e3_ms int;
        declare cnt_distinct_1e3_ms int;
        declare sel_distinct_1e4_ms int;
        declare cnt_distinct_1e4_ms int;
        declare sel_distinct_1e5_ms int;
        declare cnt_distinct_1e5_ms int;
        declare n int;
        declare t0 timestamp;
    begin
        t0='now';
        select count(*) from ( select distinct id from test1e1 ) into n;
        sel_distinct_1e1_ms = datediff(millisecond from t0 to cast('now' as timestamp));

        t0='now';
        select count(distinct id) from test1e1 into n;
        cnt_distinct_1e1_ms = datediff(millisecond from t0 to cast('now' as timestamp));

        ratio_select_vs_count_1e1 = 1.0000 * sel_distinct_1e1_ms / cnt_distinct_1e1_ms;

        ------------

        t0='now';
        select count(*) from ( select distinct id from test1e2 ) into n;
        sel_distinct_1e2_ms = datediff(millisecond from t0 to cast('now' as timestamp));

        t0='now';
        select count(distinct id) from test1e2 into n;
        cnt_distinct_1e2_ms = datediff(millisecond from t0 to cast('now' as timestamp));

        ratio_select_vs_count_1e2 = 1.0000 * sel_distinct_1e2_ms / cnt_distinct_1e2_ms;

        ------------

        t0='now';
        select count(*) from ( select distinct id from test1e3 ) into n;
        sel_distinct_1e3_ms = datediff(millisecond from t0 to cast('now' as timestamp));

        t0='now';
        select count(distinct id) from test1e3 into n;
        cnt_distinct_1e3_ms = datediff(millisecond from t0 to cast('now' as timestamp));

        ratio_select_vs_count_1e3 = 1.0000 * sel_distinct_1e3_ms / cnt_distinct_1e3_ms;

        ------------

        t0='now';
        select count(*) from ( select distinct id from test1e4 ) into n;
        sel_distinct_1e4_ms = datediff(millisecond from t0 to cast('now' as timestamp));

        t0='now';
        select count(distinct id) from test1e4 into n;
        cnt_distinct_1e4_ms = datediff(millisecond from t0 to cast('now' as timestamp));

        ratio_select_vs_count_1e4 = 1.0000 * sel_distinct_1e4_ms / cnt_distinct_1e4_ms;

        ------------

        t0='now';
        select count(*) from ( select distinct id from test1e5 ) into n;
        sel_distinct_1e5_ms = datediff(millisecond from t0 to cast('now' as timestamp));

        t0='now';
        select count(distinct id) from test1e5 into n;
        cnt_distinct_1e5_ms = datediff(millisecond from t0 to cast('now' as timestamp));

        ratio_select_vs_count_1e5 = 1.0000 * sel_distinct_1e5_ms / cnt_distinct_1e5_ms;

        ------------

        ratio_for_1e1 = 'Acceptable';
        ratio_for_1e2 = 'Acceptable';
        ratio_for_1e3 = 'Acceptable';
        ratio_for_1e4 = 'Acceptable';
        ratio_for_1e5 = 'Acceptable';

        if (1=0 or ratio_select_vs_count_1e1 > max_diff_threshold) then
            -- Example: RATIO_FOR_1E1                   Regression /* perf_issue_tag */: ratio = 3.3695 > 3.0000
            ratio_for_1e1 = 'Regression /* perf_issue_tag */: ratio = '||ratio_select_vs_count_1e1||' > '||max_diff_threshold;

        if (1=0 or ratio_select_vs_count_1e2 > max_diff_threshold) then
            ratio_for_1e2 = 'Regression /* perf_issue_tag */: ratio = '||ratio_select_vs_count_1e2||' > '||max_diff_threshold;

        if (1=0 or ratio_select_vs_count_1e3 > max_diff_threshold) then
            ratio_for_1e3 = 'Regression /* perf_issue_tag */: ratio = '||ratio_select_vs_count_1e3||' > '||max_diff_threshold;

        if (1=0 or ratio_select_vs_count_1e4 > max_diff_threshold) then
            ratio_for_1e4 = 'Regression /* perf_issue_tag */: ratio = '||ratio_select_vs_count_1e4||' > '||max_diff_threshold;

        if (1=0 or ratio_select_vs_count_1e5 > max_diff_threshold) then
            ratio_for_1e5 = 'Regression /* perf_issue_tag */: ratio = '||ratio_select_vs_count_1e5||' > '||max_diff_threshold;


        suspend;

    end
    ^ set term ;^
"""

act = isql_act('db', test_script,substitutions = [('[ \t]+', ' ')])

expected_stdout = f"""
    RATIO_FOR_1E1 Acceptable
    RATIO_FOR_1E2 Acceptable
    RATIO_FOR_1E3 Acceptable
    RATIO_FOR_1E4 Acceptable
    RATIO_FOR_1E5 Acceptable
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

