#coding:utf-8
#
# id:           bugs.core_2798
# title:        Incomplete plan output (lack of view names) when selecting from views containing procedures inside
# decription:   
# tracker_id:   CORE-2798
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table t1 (col int);
    commit;
    
    set term ^;
    create procedure p1 returns (res int) as begin suspend; end^
    set term ;^
    commit;
    
    create view v as select 1 as num from t1, t1 as t2, p1, p1 as p2;
    commit;
    set plan on;
    select * from v;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN JOIN (V P1 NATURAL, V P2 NATURAL, V T1 NATURAL, V T2 NATURAL)
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

