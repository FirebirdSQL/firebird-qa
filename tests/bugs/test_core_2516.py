#coding:utf-8
#
# id:           bugs.core_2516
# title:        Wrong processing a SP parameters with arrays
# decription:   
# tracker_id:   CORE-2516
# min_versions: []
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    create domain t_smallint_array as smallint [0:2];
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create procedure sp_smallint_array(x t_smallint_array)
     returns (y t_smallint_array)
    as
    begin
      y=x;
      suspend;
    end
    ^ set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 0A000
    CREATE PROCEDURE SP_SMALLINT_ARRAY failed
    -Dynamic SQL Error
    -feature is not supported
    -Usage of domain or TYPE OF COLUMN of array type in PSQL  """

@pytest.mark.version('>=3.0')
def test_core_2516_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

