#coding:utf-8
#
# id:           bugs.core_1716
# title:        Wrong variable initialization in recursive procedures
# decription:
# tracker_id:   CORE-1716
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    create domain dm_int as integer default 0 not null;
    commit;

    -- sample with returned variable
    set term ^;
    create procedure sp_test1(a_cnt int)
    returns (o_cnt int, o_ret dm_int)
    as
    begin
      while (a_cnt>0) do
      begin
        o_cnt = a_cnt;
        a_cnt = a_cnt-1;
        for
          select o_ret
          from sp_test1( :a_cnt )
          into o_ret
        do
          suspend;
      end
      suspend;
    end
    ^

    create procedure sp_test2(a_cnt int)
    returns (o_cnt int, o_ret dm_int)
    as
    declare x dm_int;
    begin
      while (a_cnt>0) do
      begin
        o_cnt = a_cnt;
        a_cnt = a_cnt-1;
        for
          select o_ret
          from sp_test2( :a_cnt )
          into o_ret
          do begin
            o_ret = x;
            suspend;
          end
      end
      o_ret=x;
      suspend;
    end
    ^
    set term ;^
    commit;

    select * from sp_test1(3);
    select * from sp_test2(3);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
           O_CNT        O_RET
    ============ ============
               3            0
               3            0
               3            0
               3            0
               2            0
               2            0
               1            0
               1            0


           O_CNT        O_RET
    ============ ============
               3            0
               3            0
               3            0
               3            0
               2            0
               2            0
               1            0
               1            0
"""

@pytest.mark.version('>=2.1.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

