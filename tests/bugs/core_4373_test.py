#coding:utf-8

"""
ID:          issue-4695
ISSUE:       4695
TITLE:       Duplicate names in package are not checked
DESCRIPTION:
JIRA:        CORE-4373
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^ ;

    create package new_package
    as
    begin
       procedure external_proc;
       procedure external_proc;
       procedure external_proc;
    end^


    create package body new_package
    as
    begin
      procedure external_proc as
      begin
      end

      procedure internal_proc as
      begin
      end
      procedure internal_proc as
      begin
      end
      procedure internal_proc as
      begin
      end
    end^

    set term ; ^
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    CREATE PACKAGE NEW_PACKAGE failed
    -Duplicate PROCEDURE EXTERNAL_PROC

    Statement failed, SQLSTATE = 42000
    CREATE PACKAGE BODY NEW_PACKAGE failed
    -Duplicate PROCEDURE INTERNAL_PROC
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

