#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/9019
TITLE:       stack-buffer-overflow in decNumber
DESCRIPTION:
    Test generates <N> strings based on int128 values (both positive and negative).
    Value <N> must be odd and currently equals to 101.
    Several digits remain from each string by randomly selectred count from [1...32].
    Then every such substring is casted again to int128 and is prefixed by 'NaN' or '-Nan'
    (depending on sign of original value).
    Also, we add to the test rowset two special values for zero: 'NaN' and '-NaN'
    (thus total count of numbers for both 'NaN' and '-NaN' categories will become EVEN).

    Then we make cast all random numbers and strings like 'NaN12345' and '-NaN54321' to DECFLOAT,
    with separating them on different columns depending on 'nan' = sign and 'ri' = (rownum-1)/2.
    Final grouping by 'nan' and 'ri' columns will produce rowset with values to be compared.
    This is example of what will be source to the final comparison (ini1 vs ini2 ; nan1 vs nan2):
        -------------------:------------------:-----------------------:----------------------
                  df_ini1  :         df_ini2  :              df_nan1  :               df_nan2
        -------------------:------------------:-----------------------:----------------------
          995220403781632  :             976  :   NaN995220403781632  :                NaN976
         8316144863412224  :      9535183872  :  NaN8316144863412224  :         NaN9535183872
                        0  :     93388122112  :                  NaN  :        NaN93388122112
        -802510434304      : -23169178173440  :     -NaN802510434304  :    -NaN23169178173440
        -5911903793905664  : -80896           : -NaN5911903793905664  :             -NaN80896
                        0  : -852680797018033 :                 -NaN  :   -NaN852680797018033

    Following rules must be met for each line in this table:
      * sign(df_ini1 - df_ini2) == totalorder(df_ini1, df_ini2) && totalorder(df_ini1, df_ini2) == totalorder(df_nan1, df_nan2)
      * sign(df_ini2 - df_ini1) == totalorder(df_ini2, df_ini1) && totalorder(df_ini2, df_ini1) == totalorder(df_nan2, df_nan1)
    If some line violates such rules then it will be shown and test is considered as FAILED.
NOTES:
    [02.09.2026] pzotov
    Confirmed issue on 6.0.0.2140-1b42306 (10.08.2026 20:39); 5.0.5.1868; 4.0.8.3314.
    Checked on 6.0.0.2147, 5.0.5.1879-d995e8d.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    set list on;
    set count on;
    with
    a as (
        select
            cast( rand() * 170141183460469231731687303715884105727 as int128 ) as ns
           ,maxvalue(1, cast(rand()*32 as int)) as dq
        from (select 1 i from rdb$types rows 101)
        union ALL
        select
            cast( rand() * -170141183460469231731687303715884105728 as int128 ) ns
           ,maxvalue(2, cast(rand()*32 as int)) as dq
        from (select 1 i from rdb$types rows 101)
        union DISTINCT
        -- materialize result of above shown query, needed because of rand() presense:
        select * from (select null as ns, null as dq from rdb$database rows 0)
    )
    ,b as (
        select
             maxvalue(1,cast(right(a.ns, a.dq) as int128)) as df_ini
            ,sign(a.ns) as df_sig
            ,iif( sign(a.ns) = 1, 'NaN', '-NaN' ) as nan
        from a
        UNION ALL
        select
             0 as df_ini
            ,0 as df_sig
            ,iif(i = 1, 'NaN', '-NaN') as nan
        from (select row_number()over() as i from rdb$types rows 2)
    )
    --select * from b

    ,c as (
        select
            df_ini
            ,df_sig
            ,nan
            --,trim(nan) || df_ini
            ,(row_number()over(partition by nan order by rand()) - 1) as rn
        from b
    )
    --select * from c

    ,d as (
        select
        c.*
        ,rn/2 as ri
        ,iif( mod(rn,2) = 0, df_sig * cast(df_ini as decfloat), null) as df_ini1
        ,iif( mod(rn,2) = 0, cast(trim(nan) || df_ini as decfloat), null) as df_nan1
        ,iif( mod(rn,2) = 1, df_sig * cast(df_ini as decfloat), null) as df_ini2
        ,iif( mod(rn,2) = 1, cast(trim(nan) || df_ini as decfloat), null) as df_nan2
        from c order by nan, rn
    )
    --select * from d

    ,e as (
        select
            nan
            ,ri
            ,max(df_ini1) as df_ini1
            ,max(df_ini2) as df_ini2
            ,max(df_nan1) as df_nan1
            ,max(df_nan2) as df_nan2
        from d
        group by nan, ri
    )
    --select * from e

    ,f as (
        select
            nan
            ,ri
            ,df_ini1
            ,df_ini2
            ,df_nan1
            ,df_nan2
            ,sign(df_ini1 - df_ini2) as sign_ini_1_2
            ,totalorder(df_ini1, df_ini2) as ttlo_ini_1_2
            ,totalorder(df_nan1, df_nan2) as ttlo_nan_1_2
        
            ,sign(df_ini2 - df_ini1) as sign_ini_2_1
            ,totalorder(df_ini2, df_ini1) as ttlo_ini_2_1
            ,totalorder(df_nan2, df_nan1) as ttlo_nan_2_1
        from e
    )
    ,g as (
        select
            --nan
            --,ri
             df_ini1
            ,df_ini2
            ,df_nan1
            ,df_nan2
            ,sign_ini_1_2
            ,ttlo_ini_1_2
            ,ttlo_nan_1_2
            ,sign_ini_2_1
            ,ttlo_ini_2_1
            ,ttlo_nan_2_1
            ,iif(sign_ini_1_2 = ttlo_ini_1_2 and ttlo_ini_1_2 = ttlo_nan_1_2, '   ', '### FAIL ###') as cmp_1_2
            ,iif(sign_ini_2_1 = ttlo_ini_2_1 and ttlo_ini_2_1 = ttlo_nan_2_1, '   ', '### FAIL ###') as cmp_2_1
        from f
    )
    select g.*
    from g
    where coalesce(nullif(cmp_1_2, '   '), nullif(cmp_1_2, '   ')) is not null
    ;
"""

act = isql_act('db', test_script)

expected_stdout = """
    Records affected: 0
"""

@pytest.mark.version('>=5.0.5')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
