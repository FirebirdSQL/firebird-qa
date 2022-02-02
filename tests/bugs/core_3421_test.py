#coding:utf-8

"""
ID:          issue-3784
ISSUE:       3784
TITLE:       [FB3] AV with "UPDATE OR INSERT"
DESCRIPTION:
JIRA:        CORE-3421
FBTEST:      bugs.core_3421
"""

import pytest
from firebird.qa import *

init_script = """
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

db = db_factory(init=init_script)

test_script = """
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

act = isql_act('db', test_script, substitutions=[('^((?!sqltype|DTS_DIFF).)*$', ''),
                                                   ('[ ]+', ' '), ('[\t]*', ' ')])

expected_stdout = """
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 512 charset: 0 NONE
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 512 charset: 0 NONE
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 512 charset: 0 NONE
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

