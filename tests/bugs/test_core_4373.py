#coding:utf-8
#
# id:           bugs.core_4373
# title:        Duplicate names in package are not checked
# decription:   
# tracker_id:   CORE-4373
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    CREATE PACKAGE NEW_PACKAGE failed
    -Duplicate PROCEDURE EXTERNAL_PROC

    Statement failed, SQLSTATE = 42000
    CREATE PACKAGE BODY NEW_PACKAGE failed
    -Duplicate PROCEDURE INTERNAL_PROC
  """

@pytest.mark.version('>=3.0')
def test_core_4373_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

