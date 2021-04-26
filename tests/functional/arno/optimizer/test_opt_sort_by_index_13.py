#coding:utf-8
#
# id:           functional.arno.optimizer.opt_sort_by_index_13
# title:        ORDER BY ASC using index (multi)
# decription:   WHERE X = 1 ORDER BY Y ASC
#               WHERE clause and ORDER BY nodes can sometimes be merged to get optimal result from compound index.
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.arno.optimizer.opt_sort_by_index_13

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """
    recreate table test_idx (
      id1 integer,
      id2 integer
    );
    insert into test_idx(id1, id2)
    select (r/10)*10, r - (r/10)*10
    from (select row_number()over() r from rdb$types rows 50);
    insert into test_idx (id1, id2) values (0, null);
    insert into test_idx (id1, id2) values (null, 0);
    insert into test_idx (id1, id2) values (null, null);
    commit;
    
    create asc  index idx_id1_asc      on test_idx(id1);
    create desc index idx_id1_desc     on test_idx(id1);
    create asc  index idx_id2_asc      on test_idx(id2);
    create desc index idx_id2_desc     on test_idx(id2);
    create asc  index idx_id1_id2_asc  on test_idx(id1, id2);
    create desc index idx_id1_id2_desc on test_idx(id1, id2);
    create asc  index idx_id2_id1_asc  on test_idx(id2, id1);
    create desc index idx_id2_id1_desc on test_idx(id2, id1);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Queries with RANGE index scan now have in the plan only "ORDER"
    -- clause (index navigation) without bitmap building.
    -- See: http://tracker.firebirdsql.org/browse/CORE-1550
    -- ("the same index should never appear in both ORDER and INDEX parts of the same plan item")

    set plan on;
    select t.id1, t.id2
    from test_idx t
    where t.id1 = 10      ----                               --- must navigate through the leaf level of idx_id1_id2_asc, *without* bitmap!
    order by  t.id2 asc;  ----/
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
  PLAN (T ORDER IDX_ID1_ID2_ASC)

         ID1          ID2
          10            0
          10            1
          10            2
          10            3
          10            4
          10            5
          10            6
          10            7
          10            8
          10            9
  """

@pytest.mark.version('>=3.0')
def test_opt_sort_by_index_13_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

