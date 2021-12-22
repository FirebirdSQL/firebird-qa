#coding:utf-8
#
# id:           bugs.core_6526
# title:        AV in engine when StatementTimeout is active for user statement and some internal DSQL statement was executed as part of overall execution process
# decription:   
#                   Confirmed crash on 4.0.0.2387.
#                   Checked on 4.0.0.2394 SS/CS - works OK.
#                
# tracker_id:   CORE-6526
# min_versions: ['4.0']
# versions:     4.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bail on;
    set heading off;
    set term ^;
    execute block as begin
      in autonomous transaction do
         execute statement 'set statistics index rdb$index_0';
    end
    ^
    set statement timeout 60
    ^
    execute block as begin
      in autonomous transaction do
         execute statement 'set statistics index rdb$index_0';
    end
    ^
    set term ;^
    commit;
    select 'Done.' from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Done.
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

