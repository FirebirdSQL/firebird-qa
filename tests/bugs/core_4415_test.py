#coding:utf-8

"""
ID:          issue-4737
ISSUE:       4737
TITLE:       Useless extraction of generic DDL trigger
DESCRIPTION:
JIRA:        CORE-4415
FBTEST:      bugs.core_4415
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create or alter trigger tr before any ddl statement as begin end;
    show trigger tr;
    -- Confirmed excessive output in WI-T3.0.0.30809 Firebird 3.0 Alpha 2. Was:
    -- TR, Sequence: 0, Type: BEFORE CREATE TABLE OR ALTER TABLE OR DROP TABLE OR ... OR <unknown>, Active // length = 967 characters.
"""

act = isql_act('db', test_script, substitutions=[('\\+.*', ''), ('\\=.*', ''),
                                                 ('Trigger text.*', '')])

expected_stdout = """
    TR, Sequence: 0, Type: BEFORE ANY DDL STATEMENT, Active
    as begin end
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

