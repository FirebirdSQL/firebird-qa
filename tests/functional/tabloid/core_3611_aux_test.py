#coding:utf-8
#
# id:           functional.tabloid.core_3611_aux
# title:        Wrong data while retrieving from CTEs (or derived tables) with same column names
# decription:   See another sample in this ticket (by dimitr, 30/Oct/12 07:13 PM)
# tracker_id:   CORE-3611
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;
    with tab as
    (
    select 1 as p1
    from rdb$relations
    )
    select f1.p1, f2.p1 as p2
    from tab f1 cross join tab f2
    group by f1.p1
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Invalid expression in the select list (not contained in either an aggregate function or the GROUP BY clause)
  """

@pytest.mark.version('>=2.5.2')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

