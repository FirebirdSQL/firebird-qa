#coding:utf-8
#
# id:           bugs.core_1165
# title:        WHEN <list of exceptions> tracks only the dependency on the first exception in PSQL
# decription:   
# tracker_id:   CORE-1165
# min_versions: []
# versions:     2.5.0
# qmid:         bugs.core_1165-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """recreate exception e1 'e1' ;
recreate exception e2 'e2' ;

set term ^;

create procedure p as
begin
  begin end
  when exception e1, exception e2 do
  begin
  end
end^

set term ;^
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """show depend p;

recreate exception e1 'e1';
recreate exception e2 'e2';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """[P:Procedure]
E2:Exception, E1:Exception
+++
"""
expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-cannot delete
-EXCEPTION E1
-there are 1 dependencies
Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-cannot delete
-EXCEPTION E2
-there are 1 dependencies
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

