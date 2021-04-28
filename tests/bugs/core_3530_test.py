#coding:utf-8
#
# id:           bugs.core_3530
# title:        BETWEEN operand/clause not supported for COMPUTED columns -- "feature is not supported"
# decription:   
#                  Checked on WI-V3.0.2.32670, WI-T4.0.0.503 - all fine.
#                
# tracker_id:   CORE-3530
# min_versions: ['3.0.2']
# versions:     3.0.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test2(id int);
    commit;

    recreate table test(
        x int,
        y int 
    );

    recreate table test2(
        id int,
        z computed by 
        (
           coalesce( (  select sum( 
                                     case 
                                         when (x = -1) then 
                                            999 
                                          else 
                                            (coalesce(x, 0) - coalesce(y, 0)) 
                                     end 
                                  ) 
                        from test
                        where x = test2.id
                      ), 
                      0
                    )
        )
    );
    commit;

    set plan on;
    set count on;
    --set echo on;
    -- Before 3.0.2 following statement failed with:
    -- Statement failed, SQLSTATE = 0A000
    -- feature is not supported
    select * from test2 where z between 1 and 2;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (TEST NATURAL)
    PLAN (TEST NATURAL)
    PLAN (TEST NATURAL)
    PLAN (TEST2 NATURAL)
    Records affected: 0
  """

@pytest.mark.version('>=3.0.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

