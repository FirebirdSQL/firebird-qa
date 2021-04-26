#coding:utf-8
#
# id:           bugs.core_4184
# title:        Executing empty EXECUTE BLOCK with NotNull output parameter raised error
# decription:   
# tracker_id:   CORE-4184
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    execute block
    returns (id integer not null)
    as
    begin
    end;
    -- Output in 2.5.0 ... 2.5.4:
    --          ID
    --============
    --Statement failed, SQLSTATE = 42000
    --validation error for variable ID, value "*** null ***"
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_core_4184_1(act_1: Action):
    act_1.execute()

