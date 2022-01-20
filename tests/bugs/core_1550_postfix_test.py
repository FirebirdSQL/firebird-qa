#coding:utf-8

"""
ID:          issue-1967-postfix
ISSUE:       1967
TITLE:       Unnecessary index scan happens when the same index is mapped to both WHERE and ORDER BY clauses
DESCRIPTION:
JIRA:        CORE-1550
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- sent to dimitr 30.09.14 at 22:09
    set term ^;
    execute block as
    begin
        execute statement 'drop sequence g';
        when any do begin end
    end^
    set term ;^
    commit;

    create sequence g; commit;
    recreate table td(id int primary key using index td_pk, f01 int, f02 int); commit;
    recreate table tm(id int); commit;

    insert into tm select gen_id(g,1) from rdb$types rows 100;
    commit;

    insert into td(id, f01, f02) select id, (select min(id) from tm), gen_id(g,1) from tm; commit;

    create index td_f01_non_unq on td(f01);
    create unique index td_f01_f02_unq on td(f01, f02); -- ### NB: compound UNIQUE index presens here beside of PK ###
    commit;

    set planonly;

    -- 1. Check for usage when only PK fields are involved:
    select *
    from tm m
    where exists(
        select * from td d where m.id = d.id
        order by d.id --------------------------- ### this "useless" order by should prevent from bitmap creation in 3.0+
    );
    -- Ineffective plan was here:
    -- PLAN (D ORDER TD_PK INDEX (TD_PK))
    -- ...                  ^
    --                      |
    --                      +-----> BITMAP created!

    -- 2. Check for usage when fields from UNIQUE index are involved:
    select *
    from tm m
    where exists(
        select * from td d
        where m.id = d.f01 and d.f02 = 10
        order by d.f01, d.f02 ------------------- ### this "useless" order by should prevent from bitmap creation in 3.0+
    );

    -- Ineffective plan was here:
    -- PLAN (D ORDER TD_F01_F02_UNQ INDEX (TD_F01_F02_UNQ))
    -- ...                           ^
    --                               |
    --                               +-----> BITMAP created!
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (D ORDER TD_PK)
    PLAN (M NATURAL)

    PLAN (D ORDER TD_F01_F02_UNQ)
    PLAN (M NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

