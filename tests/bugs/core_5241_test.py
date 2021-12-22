#coding:utf-8
#
# id:           bugs.core_5241
# title:        Affected rows are not counted for some update operations with views
# decription:   
#                 Confirmed big: WI-T4.0.0.184, WI-V2.5.6.27008
#                 Works fine on: WI-V3.0.1.32518, WI-T4.0.0.197
#                
# tracker_id:   CORE-5241
# min_versions: ['2.5.6']
# versions:     2.5.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate view v_test_b as select 1 i from rdb$database;
    recreate view v_test_a as select 1 i from rdb$database;
    commit;
    recreate table test (col int);
    recreate view v_test_a as select col from test;
    recreate view v_test_b as select col from v_test_a;
    commit;

    insert into test values (1);
    commit;

    set list on;

    set term ^;

    execute block returns (out_table int, out_view_a int, out_view_b int)
    as
    begin
      update test set col = 2;
      out_table = row_count;
      
      update v_test_a set col = 2;
      out_view_a = row_count;

      update v_test_b set col = 2;
      out_view_b = row_count;

      suspend;

    end^

    recreate trigger v_test_a_bu for v_test_a before update as begin end^
    recreate trigger v_test_b_bu for v_test_b before update as begin end^
    commit^

    execute block returns (out_table int, out_view_a int, out_view_b int)
    as
    begin


      update test set col = 2;
      out_table = row_count;
      
      update v_test_a set col = 2;
      out_view_a = row_count;

      update v_test_b set col = 2;
      out_view_b = row_count;

      suspend;

    end^

    execute block returns (out_table int, out_view_a int, out_view_b int)
    as
    begin
      
      update v_test_a set col = 2;
      out_view_a = row_count;

      update v_test_b set col = 2;
      out_view_b = row_count;


      update test set col = 2;
      out_table = row_count;
      
      suspend;

    end^

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    OUT_TABLE                       1
    OUT_VIEW_A                      1
    OUT_VIEW_B                      1

    OUT_TABLE                       1
    OUT_VIEW_A                      1
    OUT_VIEW_B                      1

    OUT_TABLE                       1
    OUT_VIEW_A                      1
    OUT_VIEW_B                      1
"""

@pytest.mark.version('>=2.5.6')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

