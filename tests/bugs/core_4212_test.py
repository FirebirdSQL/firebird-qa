#coding:utf-8

"""
ID:          issue-4537
ISSUE:       4537
TITLE:       Dropping FK on GTT crashes server
DESCRIPTION:
JIRA:        CORE-4212
FBTEST:      bugs.core_4212
"""

import pytest
from firebird.qa import *

db = db_factory(from_backup='core4212.fbk')

test_script = """
--  'database': 'Existing',
--  'database_name': 'core4212-25.fdb',

    set autoddl off;
    commit;
    alter table t2 drop constraint t2_fk;
    rollback;
    show table t2;
"""

act = isql_act('db', test_script)

expected_stdout = """
    ID                              VARCHAR(8) Nullable
    CONSTRAINT T2_FK:
      Foreign key (ID)    References T1 (ID)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
