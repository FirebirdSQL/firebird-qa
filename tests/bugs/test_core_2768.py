#coding:utf-8
#
# id:           bugs.core_2768
# title:        ALTERING OR DROPPING PROCEDURE which has type of domain parameter leads to attempt to delete that domain
# decription:   
#                 Checked on:
#                   4.0.0.1763 SS: 1.484s.
#                   3.0.6.33240 SS: 0.674s.
#                   2.5.9.27149 SC: 0.328s.
#                   2.5.0.26074 CS: 0.706s.
#                 
# tracker_id:   CORE-2768
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate view v_fields as
    select rf.rdb$field_name f_name, rf.rdb$field_length f_length, rf.rdb$field_type f_type
    from rdb$database r
    left join rdb$fields rf on rf.rdb$field_name = upper('dm_test')
    ;

    recreate view v_dependencies as
    select rd.rdb$dependent_name as dep_obj_name, rd.rdb$depended_on_name as dep_on_what
    from rdb$database r
    left join rdb$dependencies rd on rd.rdb$dependent_name = upper('sp_test')
    ;

    create or alter procedure sp_test as begin end
    ;
    set term ^;
    execute block as
    begin
        begin
            execute statement 'drop domain dm_test';
            when any do begin end
        end
    end
    ^
    set term ;^
    commit;

    create domain dm_test int;
    commit;
    create or alter procedure sp_test( a_01 type of dm_test ) as begin end;
    commit;

    set count on;
    set list on;

    select * from v_fields ;
    select * from v_dependencies ;
    commit;

    alter procedure sp_test as begin end;
    commit; -- here was error in 2.5 Beta 2, 2.5 RC1 

    select * from v_fields ;
    select * from v_dependencies ;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    F_NAME                          DM_TEST
    F_LENGTH                        4
    F_TYPE                          8


    Records affected: 1

    DEP_OBJ_NAME                    SP_TEST
    DEP_ON_WHAT                     DM_TEST


    Records affected: 1

    F_NAME                          DM_TEST
    F_LENGTH                        4
    F_TYPE                          8


    Records affected: 1

    DEP_OBJ_NAME                    <null>
    DEP_ON_WHAT                     <null>


    Records affected: 1
  """

@pytest.mark.version('>=2.5.0')
def test_core_2768_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

