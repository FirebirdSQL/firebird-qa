#coding:utf-8
#
# id:           bugs.core_1811
# title:        Incorrect parser's reaction to the unquoted usage of the keyword "VALUE"
# decription:   
# tracker_id:   CORE-1811
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """recreate table T ( "VALUE" int ) ;
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """delete from T where "VALUE" = 1;
-- OK

delete from T where value = 1 ;
-- ERROR: Illegal use of keyword VALUE
-- This is correct.

delete from T where value = ? ;
-- ERROR: Data type unknown (release build) or assertion failure (debug build)
-- There should be the same error as previously (Illegal use of keyword VALUE)
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
Dynamic SQL Error
-SQL error code = -901
-Illegal use of keyword VALUE
Statement failed, SQLSTATE = 42000
Dynamic SQL Error
-SQL error code = -901
-Illegal use of keyword VALUE
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

