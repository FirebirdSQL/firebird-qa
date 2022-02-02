#coding:utf-8

"""
ID:          issue-4568
ISSUE:       4568
TITLE:       Problem with creation procedure which contain adding text in DOS864 charset
DESCRIPTION:
JIRA:        CORE-4244
FBTEST:      bugs.core_4244
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    create or alter procedure sp_test as
        declare char_one_byte char(1) character set dos864;
        declare str varchar(1000) character set dos864;
    begin
        char_one_byte='A';
        str='B';
        str=str||char_one_byte;
    end
    ^
    set term ;^
    commit;
    -- Confirmed for 2.1.7:
    -- Statement failed, SQLCODE = -802
    -- arithmetic exception, numeric overflow, or string truncation
    -- -Cannot transliterate character between character sets
    show proc sp_test;
"""

act = isql_act('db', test_script, substitutions=[('=.*', '')])

expected_stdout = """
    Procedure text:
        declare char_one_byte char(1) character set dos864;
        declare str varchar(1000) character set dos864;
    begin
        char_one_byte='A';
        str='B';
        str=str||char_one_byte;
    end
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
