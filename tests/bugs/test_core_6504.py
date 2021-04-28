#coding:utf-8
#
# id:           bugs.core_6504
# title:        Provide same results for date arithmetics when date is changed by values near +/-max(bigint)
# decription:   
#                   Checked on 4.0.0.2437 (both on Linux and Windows).
#                
# tracker_id:   
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
    set heading off;

    -- All following statements must raise SQLSTATE = 22008.
    -- On LINUX builds before 4.0.0.2437 statements NN 5 and 6
    -- did not raise error. Instead, they issued date = 2020-02-01:

    select 1 as chk_1, date '01.02.2020' +  9223372036854775807 from rdb$database;
    select 2 as chk_2, date '01.02.2020' + -9223372036854775807 from rdb$database;
    select 3 as chk_3, date '01.02.2020' -  9223372036854775807 from rdb$database;
    select 4 as chk_4, date '01.02.2020' - -9223372036854775807 from rdb$database;
    select 5 as chk_5, date '01.02.2020' + -9223372036854775808 from rdb$database;
    select 6 as chk_6, date '01.02.2020' - -9223372036854775808 from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22008
    value exceeds the range for valid dates

    Statement failed, SQLSTATE = 22008
    value exceeds the range for valid dates

    Statement failed, SQLSTATE = 22008
    value exceeds the range for valid dates

    Statement failed, SQLSTATE = 22008
    value exceeds the range for valid dates

    Statement failed, SQLSTATE = 22008
    value exceeds the range for valid dates

    Statement failed, SQLSTATE = 22008
    value exceeds the range for valid dates
  """

@pytest.mark.version('>=4.0')
def test_core_6504_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

