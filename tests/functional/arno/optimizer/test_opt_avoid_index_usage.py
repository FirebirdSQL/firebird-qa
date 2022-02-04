#coding:utf-8

"""
ID:          optimizer.avoid-index-usage
ISSUE:       3431
TITLE:       AVOID index usage in WHERE <indexed_varchar_field> = <integer_value>
DESCRIPTION:
  Samples here are from #3431.
  Confirmed usage 'PLAN INDEX ...' in FB 2.0.0.12724
JIRA:        CORE-3051
FBTEST:      functional.arno.optimizer.opt_avoid_index_usage
"""

import pytest
from firebird.qa import *

init_script = """
    recreate table t(x varchar(10), y varchar(10));
    create index t_x_asc on t(x);
    create descending index t_y_desc on t(y);
    commit;
  """

db = db_factory(init=init_script)

test_script = """
    set planonly;
    --set echo on;
    select * from t where x = 0;
    select * from t where y = 0;
    select * from t where x > 0;
    select * from t where y < 0;
    select * from t where x between 0 and 1;
    select * from t where y between 0 and 1;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (T NATURAL)
    PLAN (T NATURAL)
    PLAN (T NATURAL)
    PLAN (T NATURAL)
    PLAN (T NATURAL)
    PLAN (T NATURAL)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
