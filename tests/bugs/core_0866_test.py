#coding:utf-8

"""
ID:          issue-1257
ISSUE:       1257
TITLE:       Removing a NOT NULL constraint is not visible until reconnect
DESCRIPTION:
JIRA:        CORE-866
"""

import pytest
from firebird.qa import *

init_script = """
    recreate table test (
        id integer not null,
        col varchar(20) not null
    );
    insert into test (id, col) values (1, 'data');
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    update rdb$relation_fields
      set rdb$null_flag = null
      where (rdb$field_name = upper('col')) and (rdb$relation_name = upper('test'));
    commit;

    update test set col = null where id = 1;
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    UPDATE operation is not allowed for system table RDB$RELATION_FIELDS
    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."COL", value "*** null ***"
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

