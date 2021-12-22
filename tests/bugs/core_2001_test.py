#coding:utf-8
#
# id:           bugs.core_2001
# title:        When trying to show "conversion error", "arithmetic exception/string truncation" may appear instead, misleading the user
# decription:   
# tracker_id:   CORE-2001
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

test_script_1 = """select cast('1995' as date) from rdb$database;
select cast('1995-12-2444444444444444444444444444444' as date) from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
       CAST
===========

       CAST
==========="""
expected_stderr_1 = """Statement failed, SQLSTATE = 22018

conversion error from string "1995"

Statement failed, SQLSTATE = 22018

conversion error from string "1995-12-2444444444444444444444444444444"

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

