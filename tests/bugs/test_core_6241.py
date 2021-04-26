#coding:utf-8
#
# id:           bugs.core_6241
# title:        Values greater than number of days between 01.01.0001 and 31.12.9999 (=3652058) can be added or subtracted from DATE
# decription:   
#                   Checked on 4.0.0.1761.
#                
# tracker_id:   CORE-6241
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

    -- J4YI:
    -- select datediff( day from date '01.02.2020' to date '31.12.9999') from rdb$database; -- 2914603
    -- select datediff( day from date '01.01.0001' to date '01.02.2020') from rdb$database; -- 737455
    -- select datediff( day from date '01.01.0001' to date '31.12.9999') from rdb$database; -- 3652058
    -- set echo on;

    -- ################# 1. ADDITION ##################
                                                                                                   
    select date '01.02.2020' + 2914603 as EXPECTED_9999_12_31 from rdb$database; -- OK, as expected: 9999-12-31

    select date '01.02.2020' + 2914604 from rdb$database; -- OK, as expected: SQLSTATE = 22008 (value exceeds the range for valid dates)

    select date '01.02.2020' + 2147483647 from rdb$database; -- OK, as expected: SQLSTATE = 22008

    select date '01.02.2020' + 2147483648 from rdb$database; -- OK, as expected: SQLSTATE = 22008

    select date '01.02.2020' + 4294229840 from rdb$database; -- OK, as expected: SQLSTATE = 22008

    select date '01.02.2020' + 4294229841 from rdb$database; -- ISSUED WRONG RESULT: 0001-01-01; NB: 4294967296 - 4294229841 = 737455 -- days since 01.01.0001 to 01.02.2020

    select date '01.02.2020' + 9223372036854775807 from rdb$database; -- ISSUED WRONG RESULT: 2020-01-31


    -- ############### 2. SUBTRACTION #################

    select date '01.02.2020' - 737455 as EXPECTED_0001_01_01 from rdb$database; -- OK, as expected: 0001-01-01

    select date '01.02.2020' - 737456 from rdb$database; -- OK, as expected: SQLSTATE = 22008 (value exceeds the range for valid dates)

    select date '01.02.2020' - 2147483648 from rdb$database; -- OK, as expected: SQLSTATE = 22008

    select date '01.02.2020' - 4292052692 from rdb$database; -- OK, as expected: SQLSTATE = 22008

    select date '01.02.2020' - 4292052693 from rdb$database; -- ISSUED WRONG RESULT: 9999-12-31; NB: 4294967296 - 4292052693 = 2914603 -- days since 01.02.2020 to 31.12.9999

    select date '01.02.2020' - 9223372036854775807 from rdb$database; -- ISSUED WRONG RESULT: 2020-02-02

    select date '01.02.2020' + -9223372036854775808 from rdb$database; -- ISSUED WRONG RESULT: 2020-02-01

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    EXPECTED_9999_12_31             9999-12-31
    EXPECTED_0001_01_01             0001-01-01
  """
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
def test_core_6241_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

