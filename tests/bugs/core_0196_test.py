#coding:utf-8

"""
ID:          issue-523
ISSUE:       523
TITLE:       SYSDBA can grant non existent roles
DESCRIPTION:
JIRA:        CORE-196
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    grant no_such_role to tmp$c0196;
    commit;
    set count on;
    set list on;
    select * from rdb$user_privileges where rdb$user = upper('tmp$c0196') rows 1;
    commit;
"""

substitutions = [('Statement failed, SQLSTATE = HY000', ''), ('record not found for user:.*', '')]

act = isql_act('db', test_script, substitutions=substitutions)

expected_stdout = """
    Records affected: 0
"""

expected_stderr = """
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -GRANT failed
    -SQL role NO_SUCH_ROLE does not exist
"""

tmp_user = user_factory('db', name='tmp$c0196', password='123')

@pytest.mark.version('>=3.0')
def test_1(act: Action, tmp_user: User):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

