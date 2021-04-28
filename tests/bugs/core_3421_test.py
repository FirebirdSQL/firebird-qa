#coding:utf-8
#
# id:           bugs.core_3421
# title:        [FB3] AV with "UPDATE OR INSERT"
# decription:   
# tracker_id:   CORE-3421
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!sqltype|DTS_DIFF).)*$', ''), ('[ ]+', ' '), ('[\t]*', ' ')]

init_script_1 = """
    create or alter procedure sp_test as begin end;
    commit;
    recreate table test(
        id bigint constraint test_id_pk primary key using index test_id_pk,
        s01 varchar(512)
    );
    commit;
    
    set term ^;
    create or alter procedure sp_test( a_id type of column test.id, a_s01 type of column test.s01)
    returns(o_id type of column test.id, o_s01 type of column test.s01) 
    as
    begin
      execute statement ('update or insert into test(id, s01) values( :x, :y ) returning id, s01')
      ( x := a_id, y := a_s01 )
      into o_id, o_s01;
      suspend;
    end
    ^
    set term ;^
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set sqlda_display on;
    set planonly;
    set term ^;
    execute block returns(o_id type of column test.id, o_s01 type of column test.s01) 
    as
    begin
        execute procedure sp_test(1, rpad('',512,'9876543210mnbvcxzasdfghjklpoiuytrewq')) returning_values o_id, o_s01;
        suspend;
    end 
    ^
    set term ;^
    execute procedure sp_test(1, rpad('',512,'abcdefghjklmnopqrstuwwxyz012345678'));
    select * from sp_test(1, rpad('',512,'0123456789abcdefghjklmnopqrstuwwxyz'));
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 512 charset: 0 NONE
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 512 charset: 0 NONE
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 512 charset: 0 NONE
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

