#coding:utf-8

"""
ID:          issue-4280
ISSUE:       4280
TITLE:       Wrong results when the column with collation using option (NUMERIC-SORT=1) is in where clause
DESCRIPTION:
  Changing in 3.0, comment in tracker 05/Oct/12 04:52: NUMERIC-SORT UNIQUE indexes will
  not be usable for ORDER, only for lookups.
JIRA:        CORE-3947
"""

import pytest
from firebird.qa import *

init_script = """
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

db = db_factory(init=init_script)

test_script = """
    set plan on;
    select * from t order by s1;
    select * from t order by s2;
    select * from t order by s3 desc;
    commit;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (T ORDER T_S1_NON_UNQ)
    PLAN SORT (T NATURAL)
    PLAN SORT (T NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

