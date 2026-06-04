#coding:utf-8

"""
ID:          issue-1609
ISSUE:       1609
TITLE:       View cannot be created if its WHERE clause contains IN <subquery> with a procedure reference
DESCRIPTION:
JIRA:        CORE-1183
FBTEST:      bugs.core_1183
NOTES:
    [05.06.2026] PZOTOV
        Replaced check query to the view with 'SELECT COUNT(*)' from it because test failed on FB 6.x since
        commit bb280120 (6.0.0.1959; 2026.05.21 05:41:14) when rbdb$relation_id ceased to be used as storage
        for last created relation ID.
        Checked on 6.0.0.1992; 5.0.5.1826; 4.0.0.2109; 3.0.14.33855.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set term ^;
    create or alter procedure p
      returns (col int)
    as
    begin
      col = 1;
      suspend;
    end^
    set term ;^
    commit;

    create or alter view v_test
    as
      select
          rdb$description v_descr,
          rdb$relation_id v_rel_id,
          rdb$character_set_name v_cset_name
      from rdb$database
      where 1 in ( select col from p );
    commit;
    select count(*) as v_count from v_test;
"""
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    V_COUNT 1
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

