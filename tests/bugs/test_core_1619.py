#coding:utf-8
#
# id:           bugs.core_1619
# title:        Some aggregate functions does NOT support NULL-constant in 3-d dialect
# decription:   
# tracker_id:   CORE-1619
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select 
        avg(null)              as avg_for_null
       ,sum(null)              as sum_for_null
       ,var_samp(null)         as var_samp_for_null
       ,var_pop(null)          as var_pop_for_null
       ,stddev_samp(null)      as stddev_samp_for_null
       ,stddev_pop(null)       as stddev_pop_for_null
       ,covar_samp(null, null) as covar_samp_for_nulls
       ,covar_pop(null, null)  as covar_pop_for_nulls
       ,corr(null, null)       as corr_for_nulls
    from rdb$relations;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    AVG_FOR_NULL                    <null>
    SUM_FOR_NULL                    <null>
    VAR_SAMP_FOR_NULL               <null>
    VAR_POP_FOR_NULL                <null>
    STDDEV_SAMP_FOR_NULL            <null>
    STDDEV_POP_FOR_NULL             <null>
    COVAR_SAMP_FOR_NULLS            <null>
    COVAR_POP_FOR_NULLS             <null>
    CORR_FOR_NULLS                  <null>
  """

@pytest.mark.version('>=3.0')
def test_core_1619_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

