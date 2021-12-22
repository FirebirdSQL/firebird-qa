#coding:utf-8
#
# id:           bugs.core_5165
# title:        HAVING COUNT(*) NOT IN ( <Q> ) prevent record from appearing in outer resultset when it should be there (<Q> = resultset without nulls)
# decription:   
# tracker_id:   CORE-5165
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
    -- Confirmed proper result on: WI-V3.0.0.32418, WI-T4.0.0.98
    set list on;
    set count on;
    select 1 as check_ok
    from rdb$database r
    group by r.rdb$relation_id
    having count(*) not in (select -1 from rdb$database r2); 

    select 2 as check_ok
    from rdb$database r
    group by r.rdb$relation_id
    having count(1) not in (select -1 from rdb$database r2); 
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CHECK_OK                        1
    Records affected: 1

    CHECK_OK                        2
    Records affected: 1
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

