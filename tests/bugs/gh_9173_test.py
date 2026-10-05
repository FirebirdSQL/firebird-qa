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

"""
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    COUNT 100
    COUNT 100
    COUNT 100
    COUNT 100
"""

@pytest.mark.version('>=4')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

