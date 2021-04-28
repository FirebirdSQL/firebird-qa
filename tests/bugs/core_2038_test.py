#coding:utf-8
#
# id:           bugs.core_2038
# title:        New EXECUTE STATEMENT implementation asserts or throws an error if used both before and after commin/rollback retaining
# decription:   
# tracker_id:   CORE-2038
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

test_script_1 = """-- set transaction read write snapshot;
set term ^ ;
execute block returns (i integer)
as
begin
  execute statement 'select 1 from rdb$database' into :i;
end ^
commit retain^
execute block returns (i integer)
as
begin
  execute statement 'select 1 from rdb$database' into :i;
end ^
commit retain^
commit ^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.execute()

