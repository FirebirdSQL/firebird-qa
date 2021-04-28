#coding:utf-8
#
# id:           bugs.core_2008
# title:        NOT NULL procedure parameters
# decription:   
# tracker_id:   CORE-2008
# min_versions: []
# versions:     2.1.2
# qmid:         bugs.core_2008

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.2
# resources: None

substitutions_1 = []

init_script_1 = """
    create or alter procedure test_procedure(id int not null) as begin end;
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select rdb$parameter_name p_name, rdb$null_flag n_flag
    from rdb$procedure_parameters
    where rdb$procedure_name=upper('test_procedure');
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    P_NAME                          ID
    N_FLAG                          1
  """

@pytest.mark.version('>=2.1.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

