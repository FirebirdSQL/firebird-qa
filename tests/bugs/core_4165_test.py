#coding:utf-8
#
# id:           bugs.core_4165
# title:        Replace the hierarchical union execution with the plain one
# decription:   
# tracker_id:   CORE-4165
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('record length.*', ''), ('key length.*', '')]

init_script_1 = """
    recreate table t1(id int);
    recreate table t2(id int);
    recreate table t3(id int);
    commit;
    insert into t1 select rand()*100 from rdb$types,rdb$types;
    commit;
    insert into t2 select * from t1;
    insert into t3 select * from t1;
    commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;
    set explain on;
    
    select 0 i from t1
    union all
    select 1 from t1
    union all
    select 2 from t1
    ;
    
    
    select 0 i from t2
    union
    select 1 from t2
    union
    select 2 from t2
    ;
    
    
    select 0 i from t3
    union distinct
    select 1 from t3
    union all
    select 2 from t3
    ;
    -- Note: values in 'record length' and 'key length' should be suppressed
    -- because they contain not only size of field(s) but also db_key.
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Select Expression
        -> Union
            -> Table "T1" Full Scan
            -> Table "T1" Full Scan
            -> Table "T1" Full Scan
    
    Select Expression
        -> Unique Sort (record length: 52, key length: 8)
            -> Union
                -> Table "T2" Full Scan
                -> Table "T2" Full Scan
                -> Table "T2" Full Scan
    
    Select Expression
        -> Union
            -> Unique Sort (record length: 44, key length: 8)
                -> Union
                    -> Table "T3" Full Scan
                    -> Table "T3" Full Scan
            -> Table "T3" Full Scan
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

