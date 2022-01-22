#coding:utf-8

"""
ID:          issue-3782
ISSUE:       3782
TITLE:       Recurse leads to hangs/crash server
DESCRIPTION:
JIRA:        CORE-3419
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set autoddl off;
    commit;
    recreate table test(id int);
    commit;
    set term ^;
    -- This trigger will fire 1001 times before exception raising:
    create or alter trigger trg_trans_start
    active on transaction start position 0
    as
    begin
        in autonomous transaction do
        insert into test(id) values(1);
    end
    ^
    set term ;^
    commit;
    set transaction;
"""

act = isql_act('db', test_script, substitutions=[('line: [0-9]+, col: [0-9]+', 'line: , col: ')])

expected_stderr = """
    Statement failed, SQLSTATE = 54001
    Too many concurrent executions of the same request
    -At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' line: 5, col: 9
    At trigger 'TRG_TRANS_START' ...
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute(charset='utf8')
    assert act.clean_stderr == act.clean_expected_stderr

