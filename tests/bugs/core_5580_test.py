#coding:utf-8

"""
ID:          issue-5847
ISSUE:       5847
TITLE:       Signature of packaged functions is not checked for mismatch with [NOT] DETERMINISTIC attribute
DESCRIPTION:
JIRA:        CORE-5580
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    recreate package pk1 as
    begin
        function f1() returns int deterministic;
        function f2() returns int not deterministic;
    end
    ^
    recreate package body pk1 as
    begin
        function f1() returns int not deterministic as
        begin
            return 123;
        end

        function f2() returns int not deterministic as
        begin
            return 123 * rand();
        end

    end
    ^
    set term ;^
    commit;

    set list on;

    select pk1.f1() as f1_result from rdb$database;
    select pk1.f2() as f2_result  from rdb$database;
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -RECREATE PACKAGE BODY PK1 failed
    -Function F1 has a signature mismatch on package body PK1
    Statement failed, SQLSTATE = 2F000
    Cannot execute function F1 of the unimplemented package PK1
    Statement failed, SQLSTATE = 2F000
    Cannot execute function F2 of the unimplemented package PK1
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
