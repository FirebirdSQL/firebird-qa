#coding:utf-8
#
# id:           bugs.core_6218
# title:        COUNT(DISTINCT <DECFLOAT_FIELD>) leads FB to crash when there are duplicate values of this field
# decription:   
#                   Checked on 4.0.0.1731
#                
# tracker_id:   CORE-6218
# min_versions: ['4.0']
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
    recreate table test(n decfloat);
    commit;

    insert into test values( 0 );
    insert into test values( 0 );
    commit;

    set list on;
    set explain on;

    select n as n_grouped_from_test0 from test group by 1; --- [ 1 ]
    select distinct n as n_uniq_from_test0 from test; -- [ 2 ]
    select count(distinct n) as count_uniq_from_test0 from test; -- [ 3 ] 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Select Expression
        -> Aggregate
            -> Sort (record length: 68, key length: 24)
                -> Table "TEST" Full Scan

    N_GROUPED_FROM_TEST0                                                     0



    Select Expression
        -> Unique Sort (record length: 68, key length: 24)
            -> Table "TEST" Full Scan

    N_UNIQ_FROM_TEST0                                                        0



    Select Expression
        -> Aggregate
            -> Table "TEST" Full Scan

    COUNT_UNIQ_FROM_TEST0           1
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

