#coding:utf-8

"""
ID:          issue-2548
ISSUE:       2548
TITLE:       Query plan is missing for the long query
DESCRIPTION:
JIRA:        CORE-2115
FBTEST:      bugs.core_2115
"""

import pytest
from zipfile import Path
from firebird.qa import *

db = db_factory()

act = python_act('db')

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    # Read script and expected stdout from zip file
    datafile = Path(act.files_dir / 'core_2115.zip',
                    at='tmp_core_2115_queries_with_long_plans.sql')
    act.script = datafile.read_text()
    datafile = Path(act.files_dir / 'core_2115.zip',
                    at='tmp_core_2115_check_txt_of_long_plans.log')
    act.expected_stdout = datafile.read_text()
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
