#coding:utf-8

"""
ID:          issue-5081
ISSUE:       5081
TITLE:       Command `SHOW TABLE` fails when the table contains field with unicode collationin its DDL
DESCRIPTION:
JIRA:        CORE-4782
FBTEST:      bugs.core_4782
"""

import pytest
from firebird.qa import *

db = db_factory(charset='UTF8')

test_script = """
    -- NB: it was connection charset = UTF8 that causes error, title of ticket should be changed.
    create view v_test as select d.rdb$relation_id from rdb$database d;
    commit;
    show view v_test;
"""

act = isql_act('db', test_script, substitutions=[('=.*', '')])

expected_stdout = """
    RDB$RELATION_ID                 (RDB$RELATION_ID) SMALLINT Nullable
    View Source:
    ==== ======
    select d.rdb$relation_id from rdb$database d
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

