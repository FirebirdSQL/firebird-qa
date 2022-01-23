#coding:utf-8

"""
ID:          issue-4528
ISSUE:       4528
TITLE:       Cannot create packaged routines with [VAR]CHAR parameters
DESCRIPTION:
JIRA:        CORE-4203
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    create package test1 as
    begin
       function f1(x char(3)) returns char(6) ;
    end
    ^
    commit ^

    create package body test1 as
    begin
        function f1(x char(3)) returns char(6) as
        begin
            return x;
        end
    end
    ^

    show package test1
    ^
"""

act = isql_act('db', test_script)

expected_stdout = """
    TEST1
    Header source:
    begin
           function f1(x char(3)) returns char(6) ;
        end

    Body source:
    begin
            function f1(x char(3)) returns char(6) as
            begin
                return x;
            end
        end
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

