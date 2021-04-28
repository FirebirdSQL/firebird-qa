#coding:utf-8
#
# id:           bugs.core_2538
# title:        PSQL doesnt allow to use singleton query result as input parameter of stored procedure when procedure accessed using 'execute procedure'
# decription:   
# tracker_id:   CORE-2538
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """set term ^ ;

create procedure P (I integer)
returns (O integer)
AS
BEGIN
  SUSPEND;
END ^
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """set term ^ ;

execute block
as
declare variable i integer;
begin
  select 1 from P((select 1 from rdb$database)) into :i;
end ^

execute block
as
declare variable i integer;
begin
  execute procedure P((select 1 from rdb$database)) returning_values :i;
end ^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.execute()

