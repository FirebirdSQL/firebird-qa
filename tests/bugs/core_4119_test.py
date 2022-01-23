#coding:utf-8

"""
ID:          issue-4447
ISSUE:       4447
TITLE:       Metadata source becomes wrong after twice transliteration to the metadata charset
DESCRIPTION:
JIRA:        CORE-4119
"""

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory(charset='WIN1251')

act = python_act('db', substitutions=[('=.*', '')])
script_file = temp_file('test_script.sql')

expected_stdout = """
    Procedure text:
    =============================================================================
    begin
    -- Моя процедура
    end
    =============================================================================
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action, script_file: Path):
    script_file.write_text("""
    set term ^;
    create procedure myproc as
    begin
        -- Моя процедура
    end^
    set term ;^
    show procedure myproc;
    """, encoding='cp1251')
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input_file=script_file, charset='WIN1251')
    assert act.clean_stdout == act.clean_expected_stdout


