#coding:utf-8

"""
ID:          issue-4492
ISSUE:       4492
TITLE:       Replace the hierarchical union execution with the plain one
DESCRIPTION:
JIRA:        CORE-4165
"""

import pytest
from firebird.qa import *

init_script = """
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

db = db_factory(init=init_script)

test_script = """
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

act = isql_act('db', test_script, substitutions=[('record length.*', ''), ('key length.*', '')])

expected_stdout = """
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
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
