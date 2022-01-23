#coding:utf-8

"""
ID:          issue-4450
ISSUE:       4450
TITLE:       Metadata export with isql (option -ex) does not export functions properly
DESCRIPTION:
JIRA:        CORE-4122
"""

import pytest
from firebird.qa import *

init_script = """
    set term ^ ;
    create or alter package PKG_TEST
    as
    begin
      function F_TEST_INSIDE_PKG
      returns smallint;
    end^
    set term ; ^

    set term ^ ;
    recreate package body PKG_TEST
    as
    begin
      function F_TEST_INSIDE_PKG
      returns smallint
      as
      begin
        return 1;
      end
    end^
    set term ; ^

    set term ^ ;
    create or alter function F_TEST_OUTSIDE_PKG
    returns smallint
    as
    begin
      return -1;
    end^

    set term ; ^
    commit;
"""

db = db_factory(init=init_script)

act = python_act('db', substitutions=[('/* CREATE DATABASE .*', '')])

expected_stdout = """
    SET SQL DIALECT 3;

    /* CREATE DATABASE 'localhost/3330:test.fdb' PAGE_SIZE 4096 DEFAULT CHARACTER SET NONE; */


    COMMIT WORK;

    COMMIT WORK;
    SET AUTODDL OFF;
    SET TERM ^ ;

    /* Stored functions headers */
    CREATE OR ALTER FUNCTION F_TEST_OUTSIDE_PKG RETURNS SMALLINT
    AS
    BEGIN END ^

    SET TERM ; ^
    COMMIT WORK;
    SET AUTODDL ON;

    COMMIT WORK;
    SET AUTODDL OFF;
    SET TERM ^ ;

    /* Package headers */

    /* Package header: PKG_TEST, Owner: SYSDBA */
    CREATE PACKAGE PKG_TEST AS
    begin
      function F_TEST_INSIDE_PKG
      returns smallint;
    end^

    SET TERM ; ^
    COMMIT WORK;
    SET AUTODDL ON;

    COMMIT WORK;
    SET AUTODDL OFF;
    SET TERM ^ ;

    /* Stored functions bodies */

    ALTER FUNCTION F_TEST_OUTSIDE_PKG RETURNS SMALLINT
    AS
    begin
      return -1;
    end ^

    SET TERM ; ^
    COMMIT WORK;
    SET AUTODDL ON;

    COMMIT WORK;
    SET AUTODDL OFF;
    SET TERM ^ ;

    /* Package bodies */

    /* Package body: PKG_TEST, Owner: SYSDBA */
    CREATE PACKAGE BODY PKG_TEST AS
    begin
      function F_TEST_INSIDE_PKG
      returns smallint
      as
      begin
        return 1;
      end
    end^

    SET TERM ; ^
    COMMIT WORK;
    SET AUTODDL ON;
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.isql(switches=['-x'])
    assert act.clean_stdout == act.clean_expected_stdout


