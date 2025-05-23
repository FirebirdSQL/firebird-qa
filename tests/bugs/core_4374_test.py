#coding:utf-8

"""
ID:          issue-4696
ISSUE:       4696
TITLE:       Truncation error when using EXECUTE STATEMENT with a blob
DESCRIPTION:
JIRA:        CORE-4374
FBTEST:      bugs.core_4374
NOTES:
    [05.05.2015] pzotov
    ::: NB :::
    Memory consumption of procedural objects under 64-bit environment is much bigger than on 32-bit one.
    This test was retyped because it was encountered that previous limit for the size of BLR is too weak:
    test failed at runtime with error "implementation limit exceeds".
    New (more rigorous) limit was found by using 64-bit FB, build LI-T3.0.0.31822: BLR can not be larger
    than ~2.35 Mb (previous: ~3.21 Mb)

    [15.05.2025] pzotov
    Removed output of approximate BLR length because its change can be valuable:
    6.0.0.778 2025.05.07 d735e65a: 2097000 bytes instead of previous 2359000.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """

    set list on;
    set term ^;
    execute block as
    begin
      execute statement 'drop procedure test_proc';
      when any do begin end
    end
    ^
    commit
    ^
    execute block as -- returns (proc_ddl_length int) as
      declare sql blob sub_type text;
      declare single_sttm varchar(10);

      -- for 32 bit:
      /***********************
      declare sn int = 32760;
      declare big_block_for_incr varchar(32760);
      declare max_length_for_big_blocks int = 1048576;
      declare small_incr_amount int = 2674; -- detected maximum for 3.0 Beta2 (WI-T3.0.0.31807)
      ***********************/

      -- for 64 bit:
      --/*
      declare sn int = 8192;
      declare big_block_for_incr varchar(8192);
      declare max_length_for_big_blocks int = 794500;
      declare small_incr_amount int = 19;
      --*/
    begin
      sql = 'create or alter procedure test_proc returns(id integer) as '||ascii_char(10)||'begin ';
      max_length_for_big_blocks = max_length_for_big_blocks - char_length(sql || 'end');

      single_sttm = 'suspend;' || ascii_char(10);
      big_block_for_incr = rpad('', trunc( sn / char_length(single_sttm) ) * char_length(single_sttm), single_sttm);

      while (max_length_for_big_blocks > sn) do
      begin
        sql = sql || big_block_for_incr;
        max_length_for_big_blocks = max_length_for_big_blocks - char_length(big_block_for_incr);
      end

      sql = sql || rpad('', small_incr_amount * char_length(single_sttm), single_sttm);
      sql = sql ||'end';

      --proc_ddl_length = octet_length(sql);
      rdb$set_context('USER_SESSION', 'PROC_DDL_LENGTH', octet_length(sql));
      --suspend;

      execute statement :SQL;

    end
    ^
    set term ;^
    commit;


    set term ^;
    execute block returns(returned_rows int, proc_ddl_length int, proc_src_length int) as
    begin
      execute statement 'select count(*) cnt from test_proc'
      into returned_rows;

      proc_ddl_length = cast( rdb$get_context('USER_SESSION', 'PROC_DDL_LENGTH') as int);

      select octet_length(rdb$procedure_source)
      from rdb$procedures where rdb$procedure_name = upper('test_proc')
      into proc_src_length;

      suspend;

    end
    ^
    set term ;^
    commit;
"""

act = isql_act('db', test_script)

expected_stdout = """
    RETURNED_ROWS                   87379
    PROC_DDL_LENGTH                 786480
    PROC_SRC_LENGTH                 786420
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

