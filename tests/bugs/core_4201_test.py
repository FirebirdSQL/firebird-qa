#coding:utf-8
#
# id:           bugs.core_4201
# title:        Regression: Computed field returns null value inside BI trigger
# decription:   
# tracker_id:   CORE-4201
# min_versions: ['2.0']
# versions:     2.0.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.7
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test (
        field1 integer not null,
        fld_calc computed by (field1+1),
        field2 integer
    );
    commit;
    
    set term ^ ;
    
    create trigger test_bi0 for test
    active before insert position 0
    as
    begin
      new.field2 = new.fld_calc;
      rdb$set_context('USER_TRANSACTION','NEW_FLD1', new.field1);
      rdb$set_context('USER_TRANSACTION','FLD_CALC', new.fld_calc);
      rdb$set_context('USER_TRANSACTION','NEW_FLD2', new.field2);
    end
    ^
    set term ; ^
    commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    insert into test (field1) values (1); 
    
    set list on;
    select
       cast(rdb$get_context('USER_TRANSACTION','NEW_FLD1') as bigint) as new_fld1
      ,cast(rdb$get_context('USER_TRANSACTION','FLD_CALC') as bigint) as fld_calc
      ,cast(rdb$get_context('USER_TRANSACTION','NEW_FLD2') as bigint) as new_fld2
    from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    NEW_FLD1                        1
    FLD_CALC                        2
    NEW_FLD2                        2
"""

@pytest.mark.version('>=2.0.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

