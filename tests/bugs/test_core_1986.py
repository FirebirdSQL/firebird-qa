#coding:utf-8
#
# id:           bugs.core_1986
# title:        Altering domains name drops dependencies using the domain
# decription:   
# tracker_id:   CORE-1986
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE DOMAIN D_SOME AS INTEGER;

CREATE OR ALTER PROCEDURE SP_SOME(
    SOME_PARAM D_SOME)
AS
BEGIN
END;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """ALTER DOMAIN D_SOME TO D_OTHER;

execute procedure SP_SOME (1);
commit;
execute procedure SP_SOME (1);
commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-cannot delete
-DOMAIN D_SOME
-there are 1 dependencies
"""

@pytest.mark.version('>=2.5.0')
def test_core_1986_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

