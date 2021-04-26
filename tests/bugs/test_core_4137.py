#coding:utf-8
#
# id:           bugs.core_4137
# title:        Wrong metadata output script generate by isql / CHARACTER SETISO8859_1 sintax error
# decription:   NB: missed space in the clause CHARACTER SET<SPACE>ISO8859_1
# tracker_id:   CORE-4137
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('.*CREATE DATABASE.*', '')]

init_script_1 = """"""

db_1 = db_factory(charset='ISO8859_1', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  sql_ddl='''
#      alter character set iso8859_1 set default collation pt_br;
#      commit;
#      
#      set term ^ ;
#      create or alter procedure test (
#          p01 char(10) character set iso8859_1
#      ) returns (
#          o01 varchar(30) character set iso8859_1
#      ) as begin 
#      exit; 
#      end
#      ^
#      set term ;^
#      commit;
#  '''
#  runProgram('isql',[dsn, '-ch', 'iso8859_1'], sql_ddl)
#  runProgram('isql',['-x',dsn])
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SET SQL DIALECT 3;
    /*  Character sets */
    ALTER CHARACTER SET ISO8859_1 SET DEFAULT COLLATION PT_BR;
    COMMIT WORK;
    COMMIT WORK;
    SET AUTODDL OFF;
    SET TERM ^ ;
    /* Stored procedures headers */
    CREATE OR ALTER PROCEDURE TEST (P01 CHAR(10) CHARACTER SET ISO8859_1)
    RETURNS (O01 VARCHAR(30) CHARACTER SET ISO8859_1)
    AS
    BEGIN EXIT; END ^
    SET TERM ; ^
    COMMIT WORK;
    SET AUTODDL ON;
    COMMIT WORK;
    SET AUTODDL OFF;
    SET TERM ^ ;
    /* Stored procedures bodies */
    ALTER PROCEDURE TEST (P01 CHAR(10) CHARACTER SET ISO8859_1)
    RETURNS (O01 VARCHAR(30) CHARACTER SET ISO8859_1)
    AS
    begin
    exit;
    end ^
    SET TERM ; ^
    COMMIT WORK;
    SET AUTODDL ON;
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_core_4137_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


