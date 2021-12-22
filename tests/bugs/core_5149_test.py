#coding:utf-8
#
# id:           bugs.core_5149
# title:        Regression: LEFT JOIN incorrectly pushes COALESCE into the inner stream causing wrong results
# decription:   
# tracker_id:   CORE-5149
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
    -- Confirmed: wrong result on WI-V3.0.0.32380; works fine on LI-V3.0.0.32381.
    recreate table t_stock ( 
        tnr varchar(16), 
        amount integer 
    ); 

    recreate table t_main ( 
        tnr varchar(16) primary key using index t_main_tnr, 
        minb integer 
    ); 
      
    alter table t_stock 
        add constraint fk_t_stock_1 
        foreign key (tnr) references t_main (tnr) 
        on delete cascade on update cascade
        using index t_stock_tnr
    ;
    commit;
        
    insert into t_main (tnr, minb) values ('aaa', 0); 
    insert into t_main (tnr, minb) values ('bbb', 10); 
    insert into t_main (tnr, minb) values ('ccc', 10); 
    insert into t_main (tnr, minb) values ('ddd', 10); 
      
    insert into t_stock (tnr, amount) values ('aaa', 100); 
    insert into t_stock (tnr, amount) values ('bbb', 5); 
    insert into t_stock (tnr, amount) values ('ccc', 15); 
    commit; 
      
    set list on;

    select 
        a.tnr
        ,a.minb
        ,b.amount as b_amount
        ,coalesce(b.amount,0) as coalesce_b_amt
    from t_main a 
    left join t_stock b on a.tnr = b.tnr
    where a.minb > coalesce(b.amount,0)
    order by a.tnr
    ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TNR                             bbb
    MINB                            10
    B_AMOUNT                        5
    COALESCE_B_AMT                  5

    TNR                             ddd
    MINB                            10
    B_AMOUNT                        <null>
    COALESCE_B_AMT                  0
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

