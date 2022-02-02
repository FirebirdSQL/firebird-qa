#coding:utf-8

"""
ID:          issue-3905
ISSUE:       3905
TITLE:       Database corruption after end of session : page xxx is of wrong type expected 4 found 7
DESCRIPTION:
JIRA:        CORE-3549
FBTEST:      bugs.core_3549
"""

import pytest
from firebird.qa import *

# Calculation depends on page_size=4096 !!!
db = db_factory(page_size=4096)

test_script = """
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

act = isql_act('db', test_script)

expected_stdout = """
    PG_TYPE                         3
    PG_SEQ_DISTINCT                 1
    PG_TYPE                         3
    PG_SEQ_DISTINCT                 2
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

