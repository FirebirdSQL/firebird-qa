#coding:utf-8
#
# id:           bugs.core_2501
# title:        Binary shift functions give wrong results with negative shift values
# decription:   
# tracker_id:   CORE-2501
# min_versions: ['2.5']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """select bin_shl(100, -1) from rdb$database;
select bin_shr(100, -1) from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
              BIN_SHL
=====================

              BIN_SHR
=====================
"""
expected_stderr_1 = """Statement failed, SQLSTATE = 42000

expression evaluation not supported

-Argument for BIN_SHL must be zero or positive

Statement failed, SQLSTATE = 42000

expression evaluation not supported

-Argument for BIN_SHR must be zero or positive

"""

@pytest.mark.version('>=2.5.0')
def test_core_2501_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

