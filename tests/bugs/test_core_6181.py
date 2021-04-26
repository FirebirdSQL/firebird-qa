#coding:utf-8
#
# id:           bugs.core_6181
# title:        Operations when using "SET DECFLOAT BIND BIGINT,n" with result of 11+ digits, fail with "Decimal float invalid operation"
# decription:   
#                   Confirmed bug on: 4.0.0.1633 SS: FAILED.
#                   Checked on 4.0.0.1646 CS: 1.219s.
#               
#                   10.12.2019. Updated syntax for SET BIND command because it was changed in 11-nov-2019. 
#                   Replaced 'bigint,3' with numeric(18,3) - can not specify scale using comma delimiter, i.e. ",3"
#               
#                   Checked on: WI-T4.0.0.1685.
#               
#                
# tracker_id:   CORE-6181
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
    
    -- OLD SYNTAX: set decfloat bind bigint,3;
    -- Syntax after 11-nov-2019:
    -- https://github.com/FirebirdSQL/firebird/commit/a77295ba153e0c17061e2230d0ffdbaf08839114
    -- See also: doc/sql.extensions/README.set_bind.md:
    --     SET BIND OF type-from TO { type-to | LEGACY };
    --     SET BIND OF type NATIVE;

    set bind of decfloat to numeric(18,3);

    select cast('1234567.890' as DECFLOAT(34)) as test_01 from rdb$database;
    select cast('1234567.8901' as DECFLOAT(34)) as test_02 from rdb$database;
    select cast('12345678.901' as DECFLOAT(34)) as test_03 from rdb$database; -- 12345678.901
    select cast('12345678.90' as DECFLOAT(34)) as test_04 from rdb$database; -- Expected result is: 12345678.900
    select cast('9223372036854775.807' as DECFLOAT(34)) as test_05 from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TEST_01                         1234567.890
    TEST_02                         1234567.890
    TEST_03                         12345678.901
    TEST_04                         12345678.900
    TEST_05                         9223372036854775.807
  """

@pytest.mark.version('>=4.0')
def test_core_6181_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

