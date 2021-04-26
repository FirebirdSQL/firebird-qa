#coding:utf-8
#
# id:           bugs.core_4376
# title:        Preparation of erroneous DDL statement does not show the main command failed
# decription:   
#                  Checked on 4.0.0.2416; 3.0.0.32483
#                
# tracker_id:   CORE-4376
# min_versions: ['3.0.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('-At line[:]{0,1}[\\s]+[\\d]+,[\\s]+column[:]{0,1}[\\s]+[\\d]+', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
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
def test_core_4376_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

