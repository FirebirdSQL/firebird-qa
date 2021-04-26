#coding:utf-8
#
# id:           bugs.core_1181
# title:        Union returns inconsistent field names
# decription:   
# tracker_id:   CORE-1181
# min_versions: ['2.0.7']
# versions:     2.0.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test1(id numeric(15, 2));
    commit;

    recreate table test2(id double precision);
    commit;


    insert into test1 values(0);
    commit;

    insert into test2 values(1e0); ---- do NOT use 0e0! something weird occurs on linux: aux '0' in fractional part!
    commit;

   
    set list on;

    select id as test1_id 
    from test1
    group by id
    
    union
    
    select cast(0 as numeric(15,2))
    from rdb$database;

    -----------------------------------

    select id as test2_id 
    from test2
    group by id
    
    union
    
    select cast(1 as double precision)
    from rdb$database;


    -- Results were checked both on dialect 1 & 3, they are identical.
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TEST1_ID                        0.00
    TEST2_ID                        1.000000000000000
  """

@pytest.mark.version('>=2.0.7')
def test_core_1181_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

