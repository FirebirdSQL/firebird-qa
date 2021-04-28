#coding:utf-8
#
# id:           bugs.core_2881
# title:        isql should show packaged procedures and functions categorized per package
# decription:   
# tracker_id:   CORE-2881
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
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
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

