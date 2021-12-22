#coding:utf-8
#
# id:           bugs.core_4210
# title:        Preserve comments for output parameters after altering procedures
# decription:   
# tracker_id:   CORE-4210
# min_versions: ['2.5.3']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    
    create or alter procedure sp_test as begin end;
    commit;
    recreate table test(id int);
    commit;
    set term ^;
    execute block as 
    begin
      begin execute statement 'drop domain dm_int'; when any do begin end end
      begin execute statement 'drop domain dm_dts'; when any do begin end end
    end
    ^
    set term ;^
    commit;
    
    create domain dm_int int not null;
    create domain dm_dts timestamp;
    commit;
    
    recreate table test(id dm_int, dts dm_dts);
    commit;
    
    create or alter procedure sp_test (
         a_id1 dm_int,
         a_dts1 type of dm_dts
    ) returns (
         o_id1 type of column test.id,
         o_dts1 type of column test.dts
    ) as
    begin
    end
    ;
    comment on parameter sp_test.a_id1  is 'input id1';
    comment on parameter sp_test.a_dts1 is 'input timestamp1';
    comment on parameter sp_test.o_id1  is 'output id1';
    comment on parameter sp_test.o_dts1 is 'output timestamp1';
    commit;
    
    select '' "Before altering proc:" from rdb$database;
    show comments;
    
    alter procedure sp_test (
        a_id1 dm_int, ------------------- OLD name ==> old comment also has to be preserved
        a_dts2 type of column test.id
    ) returns (
        o_id1 type of column test.id, --- OLD name ==> old comment also has to be preserved
        o_dts2 type of column test.dts
    ) as
    begin
    end;
    commit;
    
    select '' "After altering proc:" from rdb$database;
    comment on parameter sp_test.a_dts2 is 'input timestamp2';
    comment on parameter sp_test.o_dts2 is 'output timestamp2';
    show comments;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Before altering proc:
    
    COMMENT ON    PROCEDURE PARAMETER SP_TEST.A_ID1 IS input id1;
    COMMENT ON    PROCEDURE PARAMETER SP_TEST.A_DTS1 IS input timestamp1;
    COMMENT ON    PROCEDURE PARAMETER SP_TEST.O_ID1 IS output id1;
    COMMENT ON    PROCEDURE PARAMETER SP_TEST.O_DTS1 IS output timestamp1;
    
    After altering proc:
    
    COMMENT ON    PROCEDURE PARAMETER SP_TEST.A_ID1 IS input id1;
    COMMENT ON    PROCEDURE PARAMETER SP_TEST.A_DTS2 IS input timestamp2;
    COMMENT ON    PROCEDURE PARAMETER SP_TEST.O_ID1 IS output id1;
    COMMENT ON    PROCEDURE PARAMETER SP_TEST.O_DTS2 IS output timestamp2;
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

