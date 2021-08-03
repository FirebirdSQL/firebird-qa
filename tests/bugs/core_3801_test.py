#coding:utf-8
#
# id:           bugs.core_3801
# title:        Warnings could be put twice in status-vector
# decription:   
# tracker_id:   CORE-3801
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=1, init=init_script_1)

test_script_1 = """
    set term ^ ;
    execute block as
        declare d date;
    begin
        d = 'now';
    end
    ^ 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    SQL warning code = 301
    -DATE data type is now called TIMESTAMP
  """

@pytest.mark.version('>=2.5.2')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

