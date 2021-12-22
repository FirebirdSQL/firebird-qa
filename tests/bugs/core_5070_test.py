#coding:utf-8
#
# id:           bugs.core_5070
# title:        Compound index cannot be used for filtering in some ORDER/GROUP BY queries
# decription:   
#                    Execution plan is the same for all avaliable FB 3.0+ builds, since Beta1.
#                    For this reason min_version = 3.0.0 rather than 3.0.5
#                    Checked on:
#                        3.0.4.33034: OK, 2.375s.
#                        3.0.5.33084: OK, 1.422s.
#                        3.0.4.33053: OK, 2.469s.
#                        4.0.0.1172: OK, 5.344s.
#                        4.0.0.1340: OK, 2.531s.
#                        4.0.0.1249: OK, 2.594s.
#                 
# tracker_id:   CORE-5070
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
    recreate table test1 (
        ia integer not null,
        id integer not null, 
        it integer not null, 
        dt date not null, 
        constraint test1_pk_ia_id primary key (ia,id)
    );

    set plan on;
    set explain on;

    select * 
    from test1 
    where 
        ia=1 and dt='01/01/2015' and it=1 
    order by id
    ; 


    select id 
    from test1 
    where 
        ia=1 and dt='01/01/2015' and it=1 
    group by id 
    ;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Select Expression
        -> Filter
            -> Table "TEST1" Access By ID
                -> Index "TEST1_PK_IA_ID" Range Scan (partial match: 1/2)

    Select Expression
        -> Aggregate
            -> Filter
                -> Table "TEST1" Access By ID
                    -> Index "TEST1_PK_IA_ID" Range Scan (partial match: 1/2)
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

