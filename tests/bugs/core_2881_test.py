#coding:utf-8

"""
ID:          issue-3265
ISSUE:       3265
TITLE:       isql should show packaged procedures and functions categorized per package
DESCRIPTION:
JIRA:        CORE-2881
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    create or alter package p1
    as
    begin
        function f(x int) returns int;
        procedure p(x int) returns(y int);
    end
    ^
    create package body p1
    as
    begin
        function f(x int) returns int as
        begin
        return 22*x;
        end
        procedure p(x int) returns(y int) as
        begin
        y = 33*x;
        suspend;
        end
    end
    ^

    create or alter package p2
    as
    begin
        function f(x int) returns int;
        procedure p(x int) returns(y int);
    end
    ^
    create package body p2
    as
    begin
        function f(x int) returns int as
        begin
        return 222*x;
        end
        procedure p(x int) returns(y int) as
        begin
        y = 333*x;
        suspend;
        end
    end
    ^
    set term ;^
    commit;

    show package p1;
    show package p2;
"""

act = isql_act('db', test_script)

expected_stdout = """
    P1
    Header source:
    begin
        function f(x int) returns int;
        procedure p(x int) returns(y int);
    end

    Body source:
    begin
        function f(x int) returns int as
        begin
        return 22*x;
        end
        procedure p(x int) returns(y int) as
        begin
        y = 33*x;
        suspend;
        end
    end
    P2
    Header source:
    begin
        function f(x int) returns int;
        procedure p(x int) returns(y int);
    end

    Body source:
    begin
        function f(x int) returns int as
        begin
        return 222*x;
        end
        procedure p(x int) returns(y int) as
        begin
        y = 333*x;
        suspend;
        end
    end
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

