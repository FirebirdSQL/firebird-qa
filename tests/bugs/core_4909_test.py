#coding:utf-8
#
# id:           bugs.core_4909
# title:        MERGE / HASH JOINs produce incorrect results when VARCHAR join keys differ only by trailing spaces
# decription:   
# tracker_id:   CORE-4909
# min_versions: ['2.5.5']
# versions:     2.5.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter view v_test as select 1  id from rdb$database;
    commit;
    recreate table test (
        v varchar(10),
        x integer
    );
    recreate table show (
        t1_v_repl varchar(10),
        t1_x integer,
        t2_v_repl varchar(10),
        t2_x integer
    );
    commit;
    
    create or alter view v_test as
    select
         replace(t1.v, ' ', '0') as t1_v_repl
        ,t1.x as t1_x
        ,replace(t2.v, ' ', '0') as t2_v_repl
        ,t2.x as t2_x
    from test t1
    join test t2 on t1.v = t2.v;
    commit;
    
    insert into test (v, x) values ('ww', 1);
    insert into test (v, x) values ('ww ', 2);
    commit;
    
    create index test_v on test(v);
    commit;
    
    alter index test_v inactive;
    commit;
    
    set list on;
    
    delete from show;
    
    --set plan on;
    insert into show
    select * from v_test;
    set plan off;
    commit;
    
    select 'index_inactive' as msg, s.* from show s order by t1_v_repl, t2_v_repl;
    commit;
    
    alter index test_v active;
    commit;
    
    delete from show;
    
    --set plan on;
    insert into show
    select * from v_test;
    set plan off;
    commit;
    
    select 'index_active' as msg, s.* from show s order by t1_v_repl, t2_v_repl;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             index_inactive
    T1_V_REPL                       ww
    T1_X                            1
    T2_V_REPL                       ww
    T2_X                            1
    
    MSG                             index_inactive
    T1_V_REPL                       ww
    T1_X                            1
    T2_V_REPL                       ww0
    T2_X                            2
    
    MSG                             index_inactive
    T1_V_REPL                       ww0
    T1_X                            2
    T2_V_REPL                       ww
    T2_X                            1
    
    MSG                             index_inactive
    T1_V_REPL                       ww0
    T1_X                            2
    T2_V_REPL                       ww0
    T2_X                            2

    MSG                             index_active
    T1_V_REPL                       ww
    T1_X                            1
    T2_V_REPL                       ww
    T2_X                            1
    
    MSG                             index_active
    T1_V_REPL                       ww
    T1_X                            1
    T2_V_REPL                       ww0
    T2_X                            2
    
    MSG                             index_active
    T1_V_REPL                       ww0
    T1_X                            2
    T2_V_REPL                       ww
    T2_X                            1
    
    MSG                             index_active
    T1_V_REPL                       ww0
    T1_X                            2
    T2_V_REPL                       ww0
    T2_X                            2
"""

@pytest.mark.version('>=2.5.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

