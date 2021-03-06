#coding:utf-8
#
# id:           bugs.core_4083
# title:        Full outer join in derived table with coalesce (iif)
# decription:   
# tracker_id:   CORE-4083
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select
      A_SOME_FIELD,
      B_SOME_FIELD,
      C_SOME_FIELD,
      COALESCE_FIELD
    from
    (
      select
        A.SOME_FIELD as A_SOME_FIELD,
        B.SOME_FIELD as B_SOME_FIELD,
        C.SOME_FIELD as C_SOME_FIELD,
        coalesce(A.SOME_FIELD, B.SOME_FIELD, c.SOME_FIELD) as COALESCE_FIELD
      from
          (select null as SOME_FIELD from RDB$DATABASE) A
          full join
          (select 1 as SOME_FIELD from RDB$DATABASE) B on B.SOME_FIELD = A.SOME_FIELD
          full join
          (select null as SOME_FIELD from RDB$DATABASE) C on C.SOME_FIELD = B.SOME_FIELD
    ) x
    order by 1,2,3,4
    ;

    select a.*, b.*
    from
      (select 1 as field1 from rdb$database) a
      full join
      (select 2 as field2 from rdb$database) b on b.field2=a.field1
    order by 1,2
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A_SOME_FIELD                    <null>
    B_SOME_FIELD                    <null>
    C_SOME_FIELD                    <null>
    COALESCE_FIELD                  <null>
    A_SOME_FIELD                    <null>
    B_SOME_FIELD                    <null>
    C_SOME_FIELD                    <null>
    COALESCE_FIELD                  <null>
    A_SOME_FIELD                    <null>
    B_SOME_FIELD                    1
    C_SOME_FIELD                    <null>
    COALESCE_FIELD                  1

    FIELD1                          <null>
    FIELD2                          2
    FIELD1                          1
    FIELD2                          <null>
  """

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

