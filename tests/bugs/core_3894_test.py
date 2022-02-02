#coding:utf-8

"""
ID:          issue-4230
ISSUE:       4230
TITLE:       Wrong numbers in error message for decreasing char/varchar columns
DESCRIPTION:
JIRA:        CORE-3894
FBTEST:      bugs.core_3894
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set autoddl off;
    recreate table test(id int);
    commit;

    alter table test add s01 varchar(8188) character set utf8;
    commit;

    alter table test alter column s01 type varchar(8189) character set utf8;
    alter table test alter column s01 type varchar(8190) character set utf8;
    alter table test alter column s01 type varchar(8189) character set utf8;
    commit;

    show table test;
"""

act = isql_act('db', test_script)

expected_stdout = """
    ID                              INTEGER Nullable
    S01                             VARCHAR(8190) CHARACTER SET UTF8 Nullable
"""

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER TABLE TEST failed
    -New size specified for column S01 must be at least 8190 characters.
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

