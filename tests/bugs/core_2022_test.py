#coding:utf-8
#
# id:           bugs.core_2022
# title:        "EXECUTE BLOCK" statement does not support "CREATE USER"
# decription:   
# tracker_id:   CORE-2022
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
execute block
as
begin
EXECUTE statement 'create user test1 password ''test1''';
EXECUTE statement 'create user test2 password ''test2''';
end ^

commit ^

execute block
as
begin
EXECUTE statement 'drop user test1';
EXECUTE statement 'drop user test2';
end ^

commit ^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.execute()

