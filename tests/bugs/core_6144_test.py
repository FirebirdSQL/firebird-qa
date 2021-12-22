#coding:utf-8
#
# id:           bugs.core_6144
# title:        Inconsistent behaviour of the NEW context variable in AFTER UPDATE OR DELETE triggers
# decription:   
#                   Confirmed problem on: 4.0.0.1607, 3.0.5.33171 and 2.5.9.27143: new.v was assigned to 1 in AD trigger.
#                   Checked on:
#                       build 4.0.0.1614: OK, 1.472s.
#                       build 3.0.5.33172: OK, 0.802s.
#                       build 2.5.9.27144: OK, 0.376s.
#                
# tracker_id:   CORE-6144
# min_versions: ['2.5.9']
# versions:     2.5.9
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.9
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table test (id integer not null primary key); 
    commit; 

    insert into test (id) values (1); 
    commit; 
    alter table test add v integer default 1 not null; 
    commit; 
    insert into test (id) values (2); 
    commit;
    create exception exc_not_null_in_AD_trigger 'new.v is NOT null in AD trigger ?!'; 
    commit;

    set term ^; 
    create or alter trigger test_null for test after update or delete as 
    begin 
        if (new.v is not null) then -- new.v should be NULL if the trigger runs after DELETE statement 
        begin
            rdb$set_context('USER_SESSION', 'AD_TRIGGER_NEW_V', new.v);
            exception exc_not_null_in_AD_trigger;
        end
    end
    ^
    set term ;^ 
    commit; 

    delete from test where id = 2; -- no errors 
    delete from test where id = 1; -- trigger throws exception 

    set list on;
    select rdb$get_context('USER_SESSION', 'AD_TRIGGER_NEW_V') as "new_v value in AD trigger:"
    from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    new_v value in AD trigger:      <null>
"""

@pytest.mark.version('>=2.5.9')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

