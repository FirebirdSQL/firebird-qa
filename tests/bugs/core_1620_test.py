#coding:utf-8
#
# id:           bugs.core_1620
# title:        Incorrect error message (column number) if the empty SQL string is prepared
# decription:   
# tracker_id:   CORE-1620
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [("-At procedure 'TEST_ES1' line:.*", '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create procedure test_es1 as 
    begin 
        execute statement ''; 
    end
    ^
    set term ;^
    commit;
    execute procedure test_es1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Unexpected end of command - line 1, column 1
    -At procedure 'TEST_ES1' line: 3, col: 9
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

