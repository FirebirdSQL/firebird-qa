#coding:utf-8
#
# id:           bugs.core_4473
# title:        Restore of pre ODS 11.1 database can leave RDB$RELATION_TYPE null
# decription:   
#                   25SC, build 2.5.8.27065: OK, 0.860s.
#                   30SS, build 3.0.3.32738: OK, 1.344s.
#                   40SS, build 4.0.0.680: OK, 1.344s.
#                
# tracker_id:   CORE-4473
# min_versions: ['2.5.8']
# versions:     2.5.8
# qmid:         bugs.core_4473

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core_4473-ods10_1.fbk', init=init_script_1)

test_script_1 = """
    -- Source DB was created under FB 1.5.6 (ODS 10.1) and contains following objects:
    -- create table test_t(x int);
    -- create view test_v(x) as select x from test_t;
    -- Value of rdb$relations.rdb$relation_type for these objects must be zero rather than null.

    set list on; 
    select rdb$relation_type 
    from rdb$relations 
    where 
        rdb$relation_name starting with upper('test') 
        and rdb$system_flag is distinct from 1
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$RELATION_TYPE               0
    RDB$RELATION_TYPE               0
  """

@pytest.mark.version('>=2.5.8')
def test_core_4473_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

