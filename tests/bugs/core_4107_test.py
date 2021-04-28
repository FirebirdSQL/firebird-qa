#coding:utf-8
#
# id:           bugs.core_4107
# title:        wrong resultset (subquery + derived table + union)
# decription:   
# tracker_id:   CORE-4107
# min_versions: ['2.1.6']
# versions:     2.1.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.6
# resources: None

substitutions_1 = [('Statement failed.*', 'Statement failed')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Fixed on FB 3.0 since 2015-07-12
    -- http://sourceforge.net/p/firebird/code/61970
    -- Checked on WI-V3.0.0.31940.
    set list on;
    select T.VAL1,
      (
        select 'something' from rdb$database where 2 = T.ID
        union
        select null from rdb$database where 1 = 0
      ) as VAL2
    from (
      select 1 as VAL1, 1 as ID from rdb$database
      union all
      select 2 as VAL1, 2 as ID from rdb$database
    ) as T
    group by 1;

    select T.VAL1,
      min((
        select 'something' from rdb$database where 2 = T.ID
        union
        select null from rdb$database where 1 = 0
      )) as VAL2
    from (
      select 1 as VAL1, 1 as ID from rdb$database
      union all
      select 2 as VAL1, 2 as ID from rdb$database
    ) as T
    group by 1;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    VAL1                            1
    VAL2                            <null>

    VAL1                            2
    VAL2                            something
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Invalid expression in the select list (not contained in either an aggregate function or the GROUP BY clause)
  """

@pytest.mark.version('>=2.1.6')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

