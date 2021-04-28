#coding:utf-8
#
# id:           bugs.core_5974
# title:        Wrong result of select distinct with decfload/timezone/collated column
# decription:   
#                  NB: this was regression because WI-T4.0.0.1249 (build 27.10.2018) worked OK.
#                  Confirmed wrong result on 4.0.0.1340 (build 08.12.2018)
#                  Checked on: 4.0.0.1347: OK, 2.844s.
#                
# tracker_id:   CORE-5974
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
    set list on;
    recreate table test( d decfloat(34) );
    create index test_d on test(d);
    commit;

    insert into test select 15514 from rdb$types rows 3;
    commit;
    --set plan on;
    select distinct d+0 as d_distinct from test;
    select d+0 as d_grouped_nat from test group by d+0;
    select d as d_grouped_idx from test group by d;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    D_DISTINCT                                                           15514
    D_GROUPED_NAT                                                        15514
    D_GROUPED_IDX                                                        15514
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

