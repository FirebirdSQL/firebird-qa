#coding:utf-8
#
# id:           bugs.core_4434
# title:        Extend the use of colon prefix for read/assignment OLD/NEW fields and assignment to variables
# decription:   
#                   Checked on:
#                       fb30Cs, build 3.0.4.32947: OK, 1.609s.
#                       FB30SS, build 3.0.4.32963: OK, 0.843s.
#                       FB40CS, build 4.0.0.955: OK, 1.953s.
#                       FB40SS, build 4.0.0.967: OK, 1.094s.
#                
# tracker_id:   CORE-4434
# min_versions: ['3.0.0']
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
    recreate table t1(x int, n int);
    commit;
    insert into t1(x) values(777);
    commit;

    set term ^;
    create trigger t1_bu before update on t1 as
        declare v int;
    begin
        :v = :old.x * 2;
        :new.n = :v;
    end
    ^
    set term ;^
    commit;
    
    set list on;
    update t1 set x = -x rows 1;
    select * from t1;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X                               -777
    N                               1554
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

