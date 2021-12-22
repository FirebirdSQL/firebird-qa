#coding:utf-8
#
# id:           bugs.core_1592
# title:        Altering procedure parameters can lead to unrestorable database
# decription:   
#                  Checked on 4.0.0.1193 - works OK (DOES raise error during compilation).
#                
# tracker_id:   CORE-1592
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bail on;
    set list on;
    set term ^;
    create or alter procedure p2 as begin end
    ^
    commit
    ^
    create or alter procedure p1 returns ( x1 integer ) as begin
    x1 = 10; suspend;
    end 
    ^
    create or alter procedure p2 returns ( x1 integer ) as begin
    for select x1 from p1 into :x1 do suspend;
    end
    ^

    -- This should FAIL and terminate script execution:
    alter procedure p1 returns ( x2 integer ) as begin
    x2 = 10; suspend;
    end
    ^
    set term ;^
    commit;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -PARAMETER P1.X1
    -there are 1 dependencies
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

