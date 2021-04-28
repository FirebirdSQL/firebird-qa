#coding:utf-8
#
# id:           bugs.core_0858
# title:        Server crash when using UDF
# decription:   
#                   Checked on:
#                       2.5.9.27126: OK, 0.594s.
#                       3.0.5.33086: OK, 1.343s.
#                       4.0.0.1378: OK, 6.969s.
#               
#                   24.01.2019. 
#                   Disabled this test to be run on FB 4.0: added record to '%FBT_REPO%	ests\\qa4x-exclude-list.txt'.
#               
#                   UDF usage is deprecated in FB 4+, see: ".../doc/README.incompatibilities.3to4.txt".
#                   Functions div, frac, dow, sdow, getExactTimestampUTC and isLeapYear got safe replacement 
#                   in UDR library "udf_compat", see it in folder: ../plugins/udr/
#               
#                   UDF function 'sright' has direct built-in analog 'right', there is no UDR function for it.
#                
# tracker_id:   CORE-858
# min_versions: []
# versions:     3.0, 4.0
# qmid:         bugs.core_858

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bail on;
    declare external function sright
    varchar(100) by descriptor, smallint,
    varchar(100) by descriptor returns parameter 3
    entry_point 'right' module_name 'fbudf';

    commit;

    set list on;
    select 
        rdb$function_name               
        ,rdb$function_type
        ,rdb$module_name
        ,rdb$entrypoint
        ,rdb$return_argument
        ,rdb$system_flag
        ,rdb$legacy_flag
    from rdb$functions where upper(rdb$function_name) = upper('sright');

    select sright('qwerty', 2) as sright_result from rdb$database;
    commit;

    drop external function sright;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$FUNCTION_NAME               SRIGHT                                                                                       
    RDB$FUNCTION_TYPE               <null>
    RDB$MODULE_NAME                 fbudf
    RDB$ENTRYPOINT                  right                                                                                                                                                                                                                                                          
    RDB$RETURN_ARGUMENT             3
    RDB$SYSTEM_FLAG                 0
    RDB$LEGACY_FLAG                 1

    SRIGHT_RESULT                   ty
  """

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

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
def test_2(act_2: Action):
    act_2.execute()

