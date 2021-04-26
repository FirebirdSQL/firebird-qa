#coding:utf-8
#
# id:           bugs.core_1316
# title:        NOT NULL constraint for procedure parameters and variables
# decription:   
# tracker_id:   CORE-1316
# min_versions: []
# versions:     2.5
# qmid:         bugs.core_1316

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('line: \\d+, col: \\d+', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """create procedure get_something(id integer not null) as begin end;
commit;
execute procedure get_something(NULL);
execute procedure get_something(1);
set term ^;
create procedure p0(inp int) as declare i int not null; begin i = inp; end^
set term ;^
commit;
execute procedure p0(null);
execute procedure p0(1);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
validation error for variable ID, value "*** null ***"
-At procedure 'GET_SOMETHING'
Statement failed, SQLSTATE = 42000
validation error for variable I, value "*** null ***"
-At procedure 'P0' line: 1, col: 63
"""

@pytest.mark.version('>=2.5')
def test_core_1316_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

