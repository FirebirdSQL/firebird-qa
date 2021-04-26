#coding:utf-8
#
# id:           bugs.core_5217
# title:        ISQL -x may crash while exporting an exception with message text length > 127 bytes
# decription:   
#                
# tracker_id:   CORE-5217
# min_versions: ['2.5.6']
# versions:     2.5.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate exception exc_test_a 
    '1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123';

    recreate exception exc_test_b 
    '12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234';

    recreate exception exc_test_c
    '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345';

    commit;

    set list on;
    set count on;
    select rdb$exception_name, rdb$message 
    from rdb$exceptions
    order by rdb$exception_name;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$EXCEPTION_NAME              EXC_TEST_A
    RDB$MESSAGE                     1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123

    RDB$EXCEPTION_NAME              EXC_TEST_B
    RDB$MESSAGE                     12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234

    RDB$EXCEPTION_NAME              EXC_TEST_C
    RDB$MESSAGE                     123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345

    Records affected: 3
  """

@pytest.mark.version('>=2.5.6')
def test_core_5217_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

