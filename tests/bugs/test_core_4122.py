#coding:utf-8
#
# id:           bugs.core_4122
# title:        Metadata export with isql (option -ex) does not export functions properly
# decription:   
# tracker_id:   CORE-4122
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [("CREATE DATABASE '.*' PAGE_SIZE 4096 DEFAULT CHARACTER SET NONE", "CREATE DATABASE '' PAGE_SIZE 4096 DEFAULT CHARACTER SET NONE")]

init_script_1 = """
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

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# #
#  runProgram('isql',['-x',dsn,'-user',user_name,'-pass',user_password])
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SET SQL DIALECT 3; 

    /* CREATE DATABASE 'localhost/3330:C:\\FBTESTING\\qabt-repo	mp\\core4122.fdb' PAGE_SIZE 4096 DEFAULT CHARACTER SET NONE; */


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
@pytest.mark.xfail
def test_core_4122_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


