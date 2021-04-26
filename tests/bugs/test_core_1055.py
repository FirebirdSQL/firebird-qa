#coding:utf-8
#
# id:           bugs.core_1055
# title:        Wrong parameter matching for self-referenced procedures
# decription:   
# tracker_id:   CORE-1055
# min_versions: []
# versions:     2.0.1
# qmid:         bugs.core_1055

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.1
# resources: None

substitutions_1 = []

init_script_1 = """SET TERM ^;

create procedure PN (p1 int)
as
begin
  execute procedure PN (:p1);
end ^

SET TERM ;^

commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^;

alter procedure PN (p1 int, p2 int)
as
begin
  execute procedure PN (:p1, :p2);
end^

SET TERM ;^

commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.0.1')
def test_core_1055_1(act_1: Action):
    act_1.execute()

