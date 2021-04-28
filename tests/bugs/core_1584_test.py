#coding:utf-8
#
# id:           bugs.core_1584
# title:        Server crashed or bugcheck when inserting in monitoring tables.
# decription:   
# tracker_id:   CORE-1584
# min_versions: []
# versions:     2.5
# qmid:         bugs.core_1584-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    insert into mon$statements(
        mon$statement_id
        ,mon$attachment_id
        ,mon$transaction_id
        ,mon$state
        ,mon$timestamp
        ,mon$sql_text
        ,mon$stat_id
    ) values(
        1
        ,current_connection
        ,current_transaction
        ,1
        ,'now'
        ,null
        ,1
    );
    set list on;
    select 1 as x from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X                               1
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    operation not supported
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

