#coding:utf-8
#
# id:           functional.datatypes.decfloat_loose_accuracy
# title:        Test for preseving accuracy when evaluate sum of values with huge dfference in magnitude.
# decription:   
#                   Wide range of terms can lead to wrong result of sum.
#                   https://en.wikipedia.org/wiki/Decimal_floating_point
#                   https://en.wikipedia.org/wiki/Kahan_summation_algorithm
#                
# tracker_id:   
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select
         1
        +cast(1e33 as decfloat)
        -cast(1e33 as decfloat)
        as addition_with_e33
    from rdb$database;

    select
         1
        +cast(1e34 as decfloat)
        -cast(1e34 as decfloat)
        as addition_with_e34
    from rdb$database;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ADDITION_WITH_E33                                                        1
    ADDITION_WITH_E34                                                     0E+1
  """

@pytest.mark.version('>=4.0')
def test_decfloat_loose_accuracy_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

