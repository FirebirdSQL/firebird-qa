#coding:utf-8
#
# id:           bugs.core_4713
# title:        "BLOB not found" error at rollback after insert into table with expression index
# decription:   
# tracker_id:   CORE-4713
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table T1 ( bx blob sub_type text );
    
    create index t1_idx on T1 computed by (cast(substring(bx from 1 for 1000) as varchar(1000)));
    commit;
    
    set term ^;
    execute block as
        declare n int = 250;
    begin
        while (n>0) do insert into t1(bx) values( rpad( 'QWERTY', 1000, uuid_to_char(gen_uuid()) ) ) returning :n-1 into n;
    end
    ^
    set term ;^
    
    rollback;
    -- 2.5.3 (WI-V2.5.3.26780): no error.
    -- 2.5.2 (WI-V2.5.2.26540):
    --    Statement failed, SQLSTATE = HY000
    --    BLOB not found
    --    -BLOB not found
    --    -BLOB not found
    --    -BLOB not found
    --    Statement failed, SQLSTATE = 08003
    --    invalid transaction handle (expecting explicit transaction start)
    -- 2.5.1 (WI-V2.5.1.26351): 
    --    the same as 2.5.2 + crash ("08006 / -Error reading data from the connection")
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.execute()

