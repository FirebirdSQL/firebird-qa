#coding:utf-8

"""
ID:          issue-4698
ISSUE:       4698
TITLE:       Preparation of erroneous DDL statement does not show the main command failed
DESCRIPTION:
JIRA:        CORE-4376
FBTEST:      bugs.core_4376
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test1(id int, name varchar(30));
    commit;

    set term ^;
    create or alter procedure sp_test(a_id int) returns (o_name varchar(30)) as
    begin
        select text from test where id = :a_id into o_name;
        suspend;
    end
    ^

    create or alter package pkg_test as
    begin
      procedure sp_test1a(a_id int) returns (o_name varchar(30));
      procedure sp_test1b(a_id int) returns (o_name varchar(30));
      procedure sp_test1c(a_id int) returns (o_name varchar(30));
    end
    ^

    recreate package body pkg_test as
    begin

      procedure sp_test1a(a_id int) returns (o_name varchar(30)) as
      begin
        select name from test1 where id = :a_id into o_name;
        suspend;
      end

      procedure sp_test1b(a_id int) returns (o_name varchar(30)) as
      begin
        select non_existent_field from test1 where id = :a_id into o_name;
        suspend;
      end

      procedure sp_test1c(a_id int) returns (o_name varchar(30)) as
      begin
        select name from non_existent_table where id = :a_id into o_name;
        suspend;
      end
    end
    ^
"""

act = isql_act('db', test_script, substitutions=[('-At line[:]{0,1}[\\s]+[\\d]+,[\\s]+column[:]{0,1}[\\s]+[\\d]+', '')])

expected_stderr = """
    Statement failed, SQLSTATE = 42S02
    unsuccessful metadata update
    -CREATE OR ALTER PROCEDURE SP_TEST failed
    -Dynamic SQL Error
    -SQL error code = -204
    -Table unknown
    -TEST
    -At line 3, column 26
    Statement failed, SQLSTATE = 42S22
    unsuccessful metadata update
    -RECREATE PACKAGE BODY PKG_TEST failed
    -Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -NON_EXISTENT_FIELD
    -At line 12, column 16
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

