#coding:utf-8
#
# id:           bugs.core_3947
# title:        Wrong results when the column with collation using option (NUMERIC-SORT=1) is in where clause
# decription:   Changing in 3.0, comment in tracker 05/Oct/12 04:52: NUMERIC-SORT UNIQUE indexes will not be usable for ORDER, only for lookups.
# tracker_id:   CORE-3947
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    -- See also: sql.ru/forum/actualutils.aspx?action=gotomsg&tid=1093394&msg=15987488
    create collation coll_ns for utf8 from unicode 'NUMERIC-SORT=1';
    commit;
    create domain dm_ns as varchar(10) character set utf8 collate coll_ns;
    commit;
    
    recreate table t(
       s1 dm_ns
      ,s2 dm_ns
      ,s3 dm_ns
    ); commit;
    
    create index t_s1_non_unq on t(s1);
    create UNIQUE index t_s2_unq_asc on t(s2);
    create UNIQUE DESCENDING index t_s3_unq_des on t(s3);
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set plan on;
    select * from t order by s1;
    select * from t order by s2;
    select * from t order by s3 desc;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (T ORDER T_S1_NON_UNQ)
    PLAN SORT (T NATURAL)
    PLAN SORT (T NATURAL)
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

