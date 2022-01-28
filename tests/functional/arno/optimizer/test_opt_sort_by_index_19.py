#coding:utf-8

"""
ID:          optimizer.sort-by-index-19
TITLE:       ORDER BY ASC using index (multi) and WHERE clause
DESCRIPTION:
  WHERE X = 1 ORDER BY Y
  When multi-segment index is present with X as first and Y as second this index can be used.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create or alter procedure pr_filltable_53 as begin end;
    commit;

    recreate table table_53 (
      id1 integer,
      id2 integer
    );

    set term ^;
    create or alter procedure pr_filltable_53
    as
    declare variable fillid integer;
    declare variable fillid1 integer;
    begin
      fillid = 1;
      while (fillid <= 50) do
      begin
        fillid1 = (fillid / 10) * 10;
        insert into table_53
          (id1, id2)
        values
          (:fillid1, :fillid - :fillid1);
        fillid = fillid + 1;
      end
      insert into table_53 (id1, id2) values (0, null);
      insert into table_53 (id1, id2) values (null, 0);
      insert into table_53 (id1, id2) values (null, null);
    end
    ^
    set term ;^
    commit;

    execute procedure pr_filltable_53;
    commit;

    create asc index i_table_53_id1_asc on table_53 (id1);
    create desc index i_table_53_id1_desc on table_53 (id1);
    create asc index i_table_53_id2_asc on table_53 (id2);
    create desc index i_table_53_id2_desc on table_53 (id2);
    create asc index i_table_53_id1_id2_asc on table_53 (id1, id2);
    create desc index i_table_53_id1_id2_desc on table_53 (id1, id2);
    create asc index i_table_53_id2_id1_asc on table_53 (id2, id1);
    create desc index i_table_53_id2_id1_desc on table_53 (id2, id1);

    commit;

    set planonly;
    select
      t53.id2,
      t53.id1
    from table_53 t53
    where t53.id1 = 30
    order by t53.id2 asc
    ;
    -- Checked on WI-V3.0.0.32060:
    -- PLAN (T53 ORDER I_TABLE_53_ID1_ID2_ASC)
    -- Explained:
    --    Select Expression
    --        -> Filter
    --            -> Table "TABLE_53" as "T53" Access By ID
    --                -> Index "I_TABLE_53_ID1_ID2_ASC" Range Scan (partial match: 1/2)
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (T53 ORDER I_TABLE_53_ID1_ID2_ASC)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
