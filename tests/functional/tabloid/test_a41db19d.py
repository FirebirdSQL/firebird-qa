#coding:utf-8

"""
ID:          functional.tabloid.test_a41db19d
ISSUE:       n/a
TITLE:       Misc problems with custom aggregation functions.
DESCRIPTION:
    Test verifies fix for following three cases (all have been found by AI):
    1) https://groups.google.com/g/firebird-devel/c/rT3B1rUfooM
       Custom aggregate function. Accumulating problem with textual data when returning value charset is utf8
    2) https://groups.google.com/g/firebird-devel/c/ooXf6aFiJww
       Custom aggregation function which have dependant view can be unexpectedly dropped without error
    3) https://groups.google.com/g/firebird-devel/c/_xfXOaBrq-M
       Custom aggregation function. FB crashes on query to a view based on this function
NOTES:
    The fix was in:
    https://github.com/FirebirdSQL/firebird/commit/a41db19d070c6f62226f5d427258ee098f849b29
    Confirmed problems on 6.0.0.2444-4659ac9.
    Checked on 6.0.0.2444-a41db19.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- test #1
    set bail on;
    set list on;
    set autoterm on;
    create aggregate function agg_chars_concat(v varchar(10))
        returns varchar(100)
        character set utf8 -------- [ 1 ]
    as
        declare s varchar(100);
    begin
        on accumulate do
            s = coalesce(s, '') || v || ';';
        on group do
            return s;
    end;

    create aggregate function agg_last_handled(v varchar(10))
        returns varchar(100)
    as
        declare s varchar(100);
    begin
        on accumulate do
            s = v;
        on group do
            return s;
    end;
    commit;

    select agg_chars_concat(x) agg_chars_concat, agg_last_handled(x) agg_last_handled
    from (
        select 'q' x from rdb$database
        union all
        select 'w' x from rdb$database
        union all
        select 'e' x from rdb$database
    );
    commit;
    ---------------------------
    -- test #2
    set bail OFF;
    create table t2 (id integer, x integer);

    create aggregate function sum_i2(v integer)
        returns bigint
    as
        declare total bigint;
    begin
        on accumulate do total = coalesce(total,0) + coalesce(v,0);
        on group do return total;
    end;

    create view v_agg2 as select sum_i2(x) s from t2;
    commit;

    drop function sum_i2; -- must fail; before fix: silently passed.
    commit;
    ---------------------------
    -- test #3
    set bail on;
    create table t1 (id integer, x integer);
    insert into t1 values (1, 10);
    insert into t1 values (2, 20);
    commit;
    create aggregate function sum_i1(v integer)
        returns bigint
    as
        declare total bigint;
    begin
        on accumulate do total = coalesce(total,0) + coalesce(v,0);
        on group do return total;
    end;

    create view v_agg1 as select sum_i1(x) s from t1;
    commit;

    select * from v_agg1; -- caused crash before fix
"""
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    AGG_CHARS_CONCAT q;w;e;
    AGG_LAST_HANDLED e

    Statement failed, SQLSTATE = 38000
    unsuccessful metadata update
    -cannot delete
    -Function "PUBLIC"."SUM_I2"
    -there are 1 dependencies

    S 30
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
