#coding:utf-8
#
# id:           bugs.core_0209
# title:        CHECK constraints fire twice
# decription:   
# tracker_id:   CORE-0209
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [("-At trigger 'V_TEST_BIU' line.*", "-At trigger 'V_TEST_BIU' line")]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create domain dm_restricted_char as char(1) check (value in ('A','B','C', 'D','E'));
    
    recreate table test (
        id integer,
        col dm_restricted_char
    );
    
    recreate view v_test as select * from test;
    
    set term ^;
    create trigger tab_biu for test before insert or update as
    begin
        new.col = upper (new.col);
    end^

    create trigger v_test_biu for v_test before insert or update as
    begin
        -- ::: NB :::
        -- Since 2.0 trigger that belongs to updatable view MUST have DML 
        -- statement that handles underlying TABLE (this was not so in 1.5).
        if ( inserting ) then
            insert into test values( new.id, new.col );
        else
            update test set col = new.col, id = new.id 
            where id = old.id;
    end^

    set term ;^
    commit;
   
    set count on;
    set list on;
    SET ECHO ON;

    insert into v_test values (11, 'a');
    insert into v_test values (12, 'b');
    insert into v_test values (13, 'c');
    insert into v_test values (14, 'd');
    
    select * from test;
    commit;
   
    update v_test set col='e' where id=11;
    update v_test set col='e' where id=14;
    
    update test   set col='z' where id=12;
    update v_test set col='x' where id=13;
    
    select * from test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    insert into v_test values (11, 'a');
    Records affected: 1
    insert into v_test values (12, 'b');
    Records affected: 1
    insert into v_test values (13, 'c');
    Records affected: 1
    insert into v_test values (14, 'd');
    Records affected: 1

    select * from test;
    ID                              11
    COL                             A
    ID                              12
    COL                             B
    ID                              13
    COL                             C
    ID                              14
    COL                             D
    Records affected: 4
    commit;

    update v_test set col='e' where id=11;
    Records affected: 1
    update v_test set col='e' where id=14;
    Records affected: 1

    update test   set col='z' where id=12;
    Records affected: 0
    update v_test set col='x' where id=13;
    Records affected: 0

    select * from test;

    ID                              11
    COL                             E
    ID                              12
    COL                             B
    ID                              13
    COL                             C
    ID                              14
    COL                             E
    Records affected: 4
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."COL", value "Z"

    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."COL", value "X"
    -At trigger 'V_TEST_BIU' line: 8, col: 5
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

