#coding:utf-8
#
# id:           functional.datatypes.decimal_declared_scale
# title:        Declared scale does not act as a constraint, it just defines the accuracy of the storage
# decription:   
#                  Samples are from CORE-3556 and CORE-5723.
#                  Checked on:
#                      FB25SC, build 2.5.8.27090: OK, 0.453s.
#                      FB30SS, build 3.0.3.32897: OK, 1.047s.
#                      FB40SS, build 4.0.0.872: OK, 1.313s.
#                
# tracker_id:   
# min_versions: ['2.5.8']
# versions:     2.5.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    recreate table test ( id int, b numeric(18,5) );
    insert into test(id, b) values (1, 1.0000199);
    insert into test(id, b) values (2, (select round(min(b),5) from test) );
    commit;

    select id, b, iif(b = 1.00002, 'true', 'false') c from test order by id;
    commit;

    recreate table test(id int, a decimal(18,18), b decimal(3,3) );
    commit;

    insert into test(id, a, b) values( 1, '9.123456789012345678', '999999.999' );
    select * from test order by id;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    B                               1.00002
    C                               true

    ID                              2
    B                               1.00002
    C                               true

    ID                              1
    A                               9.123456789012345678
    B                               999999.999
  """

@pytest.mark.version('>=2.5.8')
def test_decimal_declared_scale_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

