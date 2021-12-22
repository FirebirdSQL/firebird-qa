#coding:utf-8
#
# id:           bugs.core_6314
# title:        Assigning RDB$DB_KEY to MBCS CHAR/VARCHAR does not enforce the target limit
# decription:   
#                  In order to prevent receiving non-ascii characters in output we try to get only octet_length of this.
#                  Confirmed bug on 3.0.6.33289, 4.0.0.1954 (get result = 2 instead of raising error).
#                  Checked on 3.0.6.33294, 4.0.0.2000 - works fine.
#                
# tracker_id:   CORE-6314
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select octet_length(x) as cast_dbkey_to_char2_length from (select cast(rdb$db_key as char(2) character set utf8) x from rdb$database);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22001
    arithmetic exception, numeric overflow, or string truncation
    -string right truncation
    -expected length 2, actual 8
"""

@pytest.mark.version('>=3.0.6')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

