#coding:utf-8
#
# id:           bugs.core_3097
# title:        Updating blob field cause server crash with ACCESS_VIOLATION exception
# decription:
#                  Checked on: WI-V2.5.6.27001, WI-V3.0.0.32487, WI-T4.0.0.141
#
# tracker_id:   CORE-3097
# min_versions: ['2.5']
# versions:     3.0
# qmid:         None

import pytest
from zipfile import Path
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              32765
    CHAR_LENGTH                     32765
    OCTET_LENGTH                    32765

    ID                              32766
    CHAR_LENGTH                     32766
    OCTET_LENGTH                    32766

    ID                              32767
    CHAR_LENGTH                     32767
    OCTET_LENGTH                    32767

    ID                              32768
    CHAR_LENGTH                     32768
    OCTET_LENGTH                    32768

    ID                              32769
    CHAR_LENGTH                     32769
    OCTET_LENGTH                    32769

    ID                              65532
    CHAR_LENGTH                     65532
    OCTET_LENGTH                    65532

    ID                              65533
    CHAR_LENGTH                     65533
    OCTET_LENGTH                    65533

    ID                              65534
    CHAR_LENGTH                     65534
    OCTET_LENGTH                    65534

    ID                              65535
    CHAR_LENGTH                     65535
    OCTET_LENGTH                    65535
"""

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -String literal with 65536 bytes exceeds the maximum length of 65535 bytes
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    script_file = Path(act_1.vars['files'] / 'core_3097.zip',
                    at='core_3097_script.sql')
    act_1.script = script_file.read_text()
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

