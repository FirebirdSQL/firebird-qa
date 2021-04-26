#coding:utf-8
#
# id:           bugs.core_2257
# title:        internal Firebird consistency check when alter dependent procedures
# decription:   
# tracker_id:   CORE-2257
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """set term ^ ;
CREATE OR ALTER PROCEDURE B
AS
begin

end ^

CREATE OR ALTER PROCEDURE A
AS
begin
  execute procedure B;
end ^

COMMIT WORK ^

execute procedure A ^

COMMIT WORK ^

CREATE OR ALTER PROCEDURE B
AS
begin

end ^

COMMIT WORK ^

execute procedure A ^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.0')
def test_core_2257_1(act_1: Action):
    act_1.execute()

