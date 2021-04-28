#coding:utf-8
#
# id:           bugs.core_4673
# title:        Computed index based on a computed column stores NULL for all its keys
# decription:   
# tracker_id:   CORE-4673
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
  recreate table tc(
       id int primary key
      ,x int
      ,y int
      ,z_expr computed by (x+y)
      ,z_noex computed by (y)
  );
  commit;
  insert into tc values( 1, 101, 201 );
  commit;
  create index tc_lpad_z_expr on tc computed by( lpad('' || z_expr , 10, 0) );

  -- Added 2nd COMPUTED_BY index WITHOUT any expression, 
  -- see dimitr's issue in the ticket, 02/Feb/15 08:52 AM.
  -- See also several samples (rus): 
  -- sql.ru/forum/actualutils.aspx?action=gotomsg&tid=945713&msg=12655568
  create index tc_lpad_z_noex on tc computed by( z_noex ); 
  commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
  set plan on;
  set list on;
  select count(*) check_cnt from tc  where tc.z_noex = 201
  union all
  select count(*) from tc  where 0 + tc.z_noex = 201
  union all
  select count(*) cnt from tc where lpad('' || tc.z_expr, 10, 0) between '0000000302' and '0000000302'
  union all
  select count(*) from tc where '' || lpad('' || tc.z_expr, 10, 0) between '0000000302' and '0000000302';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
  PLAN (TC INDEX (TC_LPAD_Z_NOEX), TC NATURAL, TC INDEX (TC_LPAD_Z_EXPR), TC NATURAL)
  CHECK_CNT                       1
  CHECK_CNT                       1
  CHECK_CNT                       1
  CHECK_CNT                       1
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

