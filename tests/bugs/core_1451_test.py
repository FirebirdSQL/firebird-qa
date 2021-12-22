#coding:utf-8
#
# id:           bugs.core_1451
# title:        Using RDB$DB_KEY in where section while selecting from a procedure crashes the server
# decription:   
# tracker_id:   CORE-1451
# min_versions: []
# versions:     2.5.0
# qmid:         bugs.core_1451-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = [('line\\s[0-9]+,', 'line x'), ('column\\s[0-9]+', 'column y')]

init_script_1 = """SET TERM ^;
create procedure test_proc
returns (A INTEGER)
as
begin
  A = 1;
  SUSPEND;
end^
SET TERM ;^
COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select * from test_proc
where rdb$db_key is not null;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42S22
Dynamic SQL Error
-SQL error code = -206
-Column unknown
-DB_KEY
-At line 2, column 7
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

