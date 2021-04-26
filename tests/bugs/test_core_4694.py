#coding:utf-8
#
# id:           bugs.core_4694
# title:        "Column unknown" error while preparing a recursive query if the recursive part contains ALIASED datasource in the join with anchor table
# decription:   Fixed on 3.0 since rev 60747, 2015-02-20 16:56:04
# tracker_id:   CORE-4694
# min_versions: ['2.5.4']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table xcall_stack (
        xcall_id int
        ,xcaller_id int
    );
    commit;
    
    set planonly;
    
    with recursive
    r as (
        select c.xcall_id
        from xcall_stack c
        where c.xcaller_id is null
    
        UNION ALL
    
        select
               c.xcall_id
        from xcall_stack c
        join r
          AS h -- <<<<<<<<<<<<<<<<<<<<<< ::: NB ::: `r` is aliased
          on c.xcaller_id = h.xcall_id
    )
    select r.xcall_id
    from r;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (R C NATURAL, R C NATURAL)
  """

@pytest.mark.version('>=3.0')
def test_core_4694_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

