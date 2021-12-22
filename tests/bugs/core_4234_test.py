#coding:utf-8
#
# id:           bugs.core_4234
# title:        Error with IF (subfunc()) when subfunc returns a boolean
# decription:   
# tracker_id:   CORE-4234
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
    set list on;
    set term ^;
    execute block returns (c integer) as
        declare variable b boolean;
        declare function f1() returns boolean as
        begin
            return true;
        end
    begin
        c = 0;
        b = f1();
        if (b) then c = 1;
        suspend;
    end
    ^
    
    execute block returns (c integer) as
        declare variable b boolean;
        declare function f1() returns boolean as
        begin
            return true;
        end
    begin
        c = 0;
        b = f1();
        if (f1()) then c = 2;
        suspend;
    end
    ^ 
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    C                               1
    C                               2
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

