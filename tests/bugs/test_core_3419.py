#coding:utf-8
#
# id:           bugs.core_3419
# title:        Recurse leads to hangs/crash server
# decription:   
# tracker_id:   CORE-3419
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = [('line: [0-9]+, col: [0-9]+', 'line: , col: ')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
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

@pytest.mark.version('>=2.5.1')
def test_core_3419_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

