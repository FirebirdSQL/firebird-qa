#coding:utf-8
#
# id:           bugs.core_4082
# title:        Wrong value of expected length in the sring right truncation error
# decription:   
#                   NB. Ticket title: Wrong error message (should point out the proper expected length)
#                
# tracker_id:   CORE-4082
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('-At block line: [\\d]+, col: [\\d]+', '-At block line')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    execute block as
        declare u varchar(14);
    begin
        u = gen_uuid();
    end
    ^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22001
    arithmetic exception, numeric overflow, or string truncation
    -string right truncation
    -expected length 14, actual 16
    -At block line: 4, col: 9
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

