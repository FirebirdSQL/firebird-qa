#coding:utf-8

"""
ID:          issue-1588
ISSUE:       1588
TITLE:       WHEN <list of exceptions> tracks only the dependency on the first exception in PSQL
DESCRIPTION:
JIRA:        CORE-1165
"""

import pytest
from firebird.qa import *

init_script = """recreate exception e1 'e1' ;
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

db = db_factory(init=init_script)

test_script = """show depend p;

recreate exception e1 'e1';
recreate exception e2 'e2';
"""

act = isql_act('db', test_script)

expected_stdout = """[P:Procedure]
E2:Exception, E1:Exception
+++
"""

expected_stderr = """Statement failed, SQLSTATE = 42000
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

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

