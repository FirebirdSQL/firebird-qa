#coding:utf-8
#
# id:           bugs.core_1371
# title:        Execute block fails within execute statement
# decription:   
# tracker_id:   CORE-1371
# min_versions: []
# versions:     2.0.2
# qmid:         bugs.core_1371

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """set term ^;
create procedure P
as
begin
  execute statement 'execute block as begin end';
end ^

set term ;^
commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.0.2')
def test_1(act_1: Action):
    act_1.execute()

