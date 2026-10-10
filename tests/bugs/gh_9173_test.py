#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9173
TITLE:       Wrong result: partial index WHERE col IS NOT NULL is applied when a comparison references a field with the same field id from another table
DESCRIPTION:
NOTES:
    [05.10.2026] pzotov
        Confirmed bug on 5.0.5.1895-9586fe7.
        Checked on 6.0.0.2197-1e316df; 5.0.5.1897-8e16604.
    [10.10.2026] pzotov
        Added example from https://github.com/FirebirdSQL/firebird/issues/9173#issuecomment-5927083279
        Confirmed problem (natural reads instead of indexed) on 6.0.0.2204-2d20c77; 5.0.5.1903-14bfcdf.
        Checked on 6.0.0.2208-6515630; 5.0.5.1906-db21868.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set bail on;

    -- T1.C and T2.T1_ID both get RDB$FIELD_ID = 2
    create table T1 (
        ID  int not null primary key,  -- field id 0
        GRP int,                       -- field id 1
        C   int                        -- field id 2, partial index
    );
    create table T2 (
        ID    int not null primary key, -- field id 0
        X     int,                      -- field id 1
        T1_ID int                       -- field id 2, same as T1.C
    );
    create table T3 (
        ID    int not null primary key, -- field id 0
        T1_ID int,                      -- field id 1, no collision
        X     int
    );
    commit;

    set term ^;
    execute block as
      declare i int = 1;
    begin
        while (i <= 1000) do
        begin
            insert into T1 (ID, GRP, C) values (:i, mod(:i, 10), iif(mod(:i, 100) = 0, :i, null));
            insert into T2 (ID, X, T1_ID) values (:i, 0, :i);
            insert into T3 (ID, T1_ID, X) values (:i, :i, 0);
            i = i + 1;
        end
    end^
    commit^

    create index T1_GRP on T1 (GRP)^
    create index T2_T1_ID on T2 (T1_ID)^
    create index T3_T1_ID on T3 (T1_ID)^
    create index T1_C on T1 (C) where C is not null^
    commit^
    set term ;^

    -- set plan on;

    -- 1. no join
    select count(*) from T1 where GRP = 0;

    -- 2. join, T2.T1_ID has the same field id as T1.C
    select count(*) from T1 join T2 on T2.T1_ID = T1.ID where T1.GRP = 0;

    -- 3. same as 2, but left join
    select count(*) from T1 left join T2 on T2.T1_ID = T1.ID where T1.GRP = 0;

    -- 4. join, T3.T1_ID has a different field id
    select count(*) from T1 join T3 on T3.T1_ID = T1.ID where T1.GRP = 0;

    -- #############################################################################
    -- Additional example:
    -- https://github.com/FirebirdSQL/firebird/issues/9173#issuecomment-5927083279
    -- Fixed 10.10.2026 as postfix:
    -- 5x: https://github.com/FirebirdSQL/firebird/commit/db21868081c07f8805758186428d342c07ddd167
    -- 6x: https://github.com/FirebirdSQL/firebird/commit/6515630a732072a38c8053cda84d4def6e158b41
    recreate table t4 (
        id integer not null primary key
        ,flag char(1)
        ,c integer
    );
    -- 1000 rows, 20 of them with flag = 'y' and c not null
    set term ^;
    execute block as
      declare i int = 1;
      declare n int = 1000;
    begin
        while (i <= n) do
        begin
            if ( i <= 50 ) then
                insert into t4 (id, flag, c) values (:i, 'y', :i);
            else
                insert into t4 (id, flag, c) values (:i, 'n', null);
            i = i + 1;
        end
    end^
    set term ;^
    commit;

    create index t4_flag_y on t4 (flag) where flag = 'y';
    create index t4_c on t4 (c) where c is not null;

    set planonly;
    select count(*) from t4 where flag = 'y';
    select count(*) from t4 where c is not null;
    select count(*) from rdb$database cross join t4 where t4.c = 50;
"""
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

@pytest.mark.version('>=4')
def test_1(act: Action):

    expected_out = """
        COUNT 100
        COUNT 100
        COUNT 100
        COUNT 100
    """

    expected_out_5x = """
        PLAN (T4 INDEX (T4_FLAG_Y))
        PLAN (T4 INDEX (T4_C))
        PLAN JOIN (RDB$DATABASE NATURAL, T4 INDEX (T4_C))
    """
    
    expected_out_6x = """
        PLAN ("PUBLIC"."T4" INDEX ("PUBLIC"."T4_FLAG_Y"))
        PLAN ("PUBLIC"."T4" INDEX ("PUBLIC"."T4_C"))
        PLAN JOIN ("SYSTEM"."RDB$DATABASE" NATURAL, "PUBLIC"."T4" INDEX ("PUBLIC"."T4_C"))
    """

    act.expected_stdout = expected_out + '\n' + (expected_out_5x if act.is_version('<6') else expected_out_6x)
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

