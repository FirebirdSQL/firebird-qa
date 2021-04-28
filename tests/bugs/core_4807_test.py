#coding:utf-8
#
# id:           bugs.core_4807
# title:        Regression: List of aggregation is not checked properly
# decription:   Field inside subquery not present in GROUP BY clause and therefore can't be used in SELECT list as is (only as argument of some aggregation function).
# tracker_id:   CORE-4807
# min_versions: ['2.5.5']
# versions:     2.5.5
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.5
# resources: None

substitutions_1 = [('SORT \\(\\(T NATURAL\\)\\)', 'SORT (T NATURAL)')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;
    select t.rdb$field_name, (select 1 from rdb$database), count(*)
    from rdb$types t
    group by t.rdb$field_name;
    
    select t.rdb$field_name, (select 1 from rdb$database where t.rdb$system_flag=1), count(*)
    from rdb$types t
    group by t.rdb$field_name;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (RDB$DATABASE NATURAL)
    PLAN SORT ((T NATURAL))
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Invalid expression in the select list (not contained in either an aggregate function or the GROUP BY clause)
  """

@pytest.mark.version('>=2.5.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

