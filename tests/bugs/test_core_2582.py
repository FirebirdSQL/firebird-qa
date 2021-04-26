#coding:utf-8
#
# id:           bugs.core_2582
# title:        Infinity from UDF should be trapped by the engine
# decription:   
#                   24.01.2019. 
#                   Disabled this test to be run on FB 4.0: added record to '%FBT_REPO%	ests\\qa4x-exclude-list.txt'.
#                   UDF usage is deprecated in FB 4+, see: ".../doc/README.incompatibilities.3to4.txt".
#                   Added EMPTY section for FB version 4.0 in this .fbt as one more way to protect from running.
#                 
# tracker_id:   CORE-2582
# min_versions: ['2.5.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    DECLARE EXTERNAL FUNCTION DPOWER
    DOUBLE PRECISION BY DESCRIPTOR, DOUBLE PRECISION BY DESCRIPTOR, DOUBLE PRECISION BY DESCRIPTOR
    RETURNS PARAMETER 3
    ENTRY_POINT 'power' MODULE_NAME 'fbudf';

    DECLARE EXTERNAL FUNCTION XASIN
    DOUBLE PRECISION
    RETURNS DOUBLE PRECISION BY VALUE
    ENTRY_POINT 'IB_UDF_asin' MODULE_NAME 'ib_udf';

    DECLARE EXTERNAL FUNCTION XDIV
    INTEGER, INTEGER
    RETURNS DOUBLE PRECISION BY VALUE
    ENTRY_POINT 'IB_UDF_div' MODULE_NAME 'ib_udf';
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select dpower(1e120, 3) from rdb$database;
    select xasin(2) from rdb$database;
    select xdiv(10, 0) from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 39000
    expression evaluation not supported
    -Floating point overflow in result from UDF DPOWER
    -UDF: DPOWER

    Statement failed, SQLSTATE = 39000
    expression evaluation not supported
    -Invalid floating point value returned by UDF XASIN
    -UDF: XASIN

    Statement failed, SQLSTATE = 39000
    expression evaluation not supported
    -Floating point overflow in result from UDF XDIV
    -UDF: XDIV
  """

@pytest.mark.version('>=3.0,<4.0')
def test_core_2582_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
     -- This section was intentionally left empty.
     -- No message should be in expected_* sections.
     -- It is STRONGLY RECOMMENDED to add this ticket
     -- in the 'excluded-list file:
     -- %FBT_REPO%	ests\\qa4x-exclude-list.txt
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)


@pytest.mark.version('>=4.0')
def test_core_2582_2(act_2: Action):
    act_2.execute()

