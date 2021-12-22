#coding:utf-8
#
# id:           bugs.core_3549
# title:        Database corruption after end of session : page xxx is of wrong type expected 4 found 7
# decription:   
# tracker_id:   CORE-3549
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- NOTE: could NOT reproduce on official 2.5.1 (WI-V2.5.1.26351, issued 03-oct-2011).
    -- Fix for this ticket in 2.5.1 was before official 2.5.1 release: 17-jul-2011, rev. 53327
    set list on;
    select rdb$page_type pg_type, count(distinct rdb$page_sequence) pg_seq_distinct
    from rdb$pages
    where rdb$relation_id = 0 and rdb$page_type=3 -- page_type = '3' --> TIP
    group by 1;
    
    commit;
    set autoddl off;
    create global temporary table gtt_test(x int) on commit preserve rows;
    create index gtt_test_x on gtt_test(x);
    commit;
    
    set term ^;
    execute block as
    declare variable i integer = 0;
    begin
      while (i < 16384) do -- start page_size * 4 transactions
      begin
        in autonomous transaction do
          execute statement 'insert into gtt_test values (1)';
        i = i + 1;
      end
    end 
    ^
    set term ;^
    
    select rdb$page_type pg_type, count(distinct rdb$page_sequence) pg_seq_distinct
    from rdb$pages
    where rdb$relation_id = 0 and rdb$page_type=3
    group by 1;
    commit;
    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PG_TYPE                         3
    PG_SEQ_DISTINCT                 1
    PG_TYPE                         3
    PG_SEQ_DISTINCT                 2
"""

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

