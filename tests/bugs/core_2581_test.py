#coding:utf-8
#
# id:           bugs.core_2581
# title:        Infinity should not escape from the engine
# decription:   
# tracker_id:   CORE-2581
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """set sql dialect 1;
select 1e161/1e-161from rdb$database;

set sql dialect 3;
select 1e308 + 1e308 from rdb$database;
select 1e308 - -1e308 from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """WARNING: Client SQL dialect has been set to 1 when connecting to Database SQL dialect 3 database.

                 DIVIDE
=======================

                    ADD
=======================

               SUBTRACT
=======================
"""
expected_stderr_1 = """Statement failed, SQLSTATE = 22003

arithmetic exception, numeric overflow, or string truncation

-Floating-point overflow.  The exponent of a floating-point operation is greater than the magnitude allowed.

Statement failed, SQLSTATE = 22003

arithmetic exception, numeric overflow, or string truncation

-Floating-point overflow.  The exponent of a floating-point operation is greater than the magnitude allowed.

Statement failed, SQLSTATE = 22003

arithmetic exception, numeric overflow, or string truncation

-Floating-point overflow.  The exponent of a floating-point operation is greater than the magnitude allowed.

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

