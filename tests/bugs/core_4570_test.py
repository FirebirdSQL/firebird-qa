#coding:utf-8
#
# id:           bugs.core_4570
# title:        Wrong error at ALTER PACKAGE
# decription:   
# tracker_id:   CORE-4570
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create package p1
    as
    begin
      function f(x int) returns int;
    end
    ^
    create package body p1
    as
    begin
      function f1(x int) returns int;
    
      function f(x int) returns int
      as
      begin
        return f1(x) * x;
      end
    
      function f1(x int) returns int
      as
      begin
         return 1;
      end
    end
    ^
    commit
    ^
    
    alter package p1
    as
    begin
      function f(x int) returns int;
      function g(x int) returns int;
    end
    ^
    commit 
    ^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.execute()

