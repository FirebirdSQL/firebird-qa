#coding:utf-8
#
# id:           bugs.core_4203
# title:        Cannot create packaged routines with [VAR]CHAR parameters
# decription:   
# tracker_id:   CORE-4203
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
    create package test1 as
    begin
       function f1(x char(3)) returns char(6) ;
    end
    ^
    commit ^

    create package body test1 as
    begin
        function f1(x char(3)) returns char(6) as
        begin
            return x;
        end
    end
    ^
    
    show package test1
    ^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TEST1                           
    Header source:
    begin
           function f1(x char(3)) returns char(6) ;
        end
    
    Body source:
    begin
            function f1(x char(3)) returns char(6) as
            begin
                return x;
            end
        end
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

