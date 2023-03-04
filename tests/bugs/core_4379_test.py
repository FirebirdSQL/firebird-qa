#coding:utf-8

"""
ID:          issue-4701
ISSUE:       4701
TITLE:       Poor performance of explicit cursors containing correlated subqueries in the select list
DESCRIPTION:
JIRA:        CORE-4379
FBTEST:      bugs.core_4379
"""

import pytest
from firebird.qa import *

init_script = """
    recreate sequence g;
    commit;
    recreate table t(id int primary key using index t_pk_idx, f01 int);
    commit;
    delete from t;
    insert into t select gen_id(g,1), gen_id(g,0)*10 from rdb$types,rdb$types
    rows 20000;
    commit;
"""

db = db_factory(from_backup='mon-stat-gathering-3_0.fbk', init=init_script)

test_script = """
    set list on;

    execute procedure sp_truncate_stat;
    commit;
    execute procedure sp_gather_stat;
    commit;

    set plan on;
    update t a set f01 = (select f01 from t x where x.id>a.id order by id rows 1);
    set plan off;
    rollback;

    execute procedure sp_gather_stat;
    commit;

    select natural_reads, indexed_reads from v_agg_stat_tabs where table_name = upper('T');

    --------------------------

    execute procedure sp_truncate_stat;
    commit;
    execute procedure sp_gather_stat;
    commit;

    set plan on;
    set term ^;
    execute block as
      declare c_cur cursor for (select (select f01 from t x where x.id>a.id order by id rows 1) as next_f01 from t a);
      declare v_next_f01 int;
    begin
      open c_cur;
      while (1=1) do
      begin
        fetch c_cur into v_next_f01;
        if (row_count = 0) then leave;
        update t set f01 = :v_next_f01 where current of c_cur;
      end
      close c_cur;
    end
    ^
    set term ;^
    set plan off;
    rollback;

    execute procedure sp_gather_stat;
    commit;

    -- On LI-T3.0.0.30981 (29-mar02014) it was 200029999  indexed reads here:
    select natural_reads, indexed_reads from v_agg_stat_tabs where table_name = upper('T');

    -----------------------------

    execute procedure sp_truncate_stat;
    commit;
    execute procedure sp_gather_stat;
    commit;

    set plan on;
    set term ^;
    execute block as
      declare v_key char(8);
      declare c_cur cursor for (select a.rdb$db_key as r_key, (select f01 from t x where x.id>a.id order by id rows 1) as next_f01 from t a);
      declare v_next_f01 int;
    begin
      open c_cur;
      while (1=1) do
      begin
        fetch c_cur into v_key, v_next_f01;
        if (row_count = 0) then leave;
        update t set f01 = :v_next_f01 where rdb$db_key = :v_key;
      end
      close c_cur;
    end
    ^
    set term ;^
    set plan off;
    rollback;

    execute procedure sp_gather_stat;
    commit;

    -- On LI-T3.0.0.30981 (29-mar02014) it was 200049999 indexed reads here:
    select natural_reads, indexed_reads from v_agg_stat_tabs where table_name = upper('T');
"""

act = isql_act('db', test_script, substitutions = [('(--\\s+)?line \\d+, col(umn)? \\d+', '')])
# -- line 2, column 7

expected_stdout = """
    PLAN (X ORDER T_PK_IDX)
    PLAN (A NATURAL)
    NATURAL_READS                   20000
    INDEXED_READS                   39999

    PLAN (C_CUR X ORDER T_PK_IDX)
    PLAN (C_CUR A NATURAL)
    PLAN (C_CUR X ORDER T_PK_IDX)
    NATURAL_READS                   20000
    INDEXED_READS                   39999

    PLAN (C_CUR X ORDER T_PK_IDX)
    PLAN (C_CUR A NATURAL)
    PLAN (C_CUR X ORDER T_PK_IDX)
    PLAN (T INDEX ())
    NATURAL_READS                   20000
    INDEXED_READS                   59999
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

