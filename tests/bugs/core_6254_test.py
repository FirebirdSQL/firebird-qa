#coding:utf-8
#
# id:           bugs.core_6254
# title:        AV in engine when using SET TRANSACTION and ON TRANSACTION START trigger uses EXECUTE STATEMENT against current transaction
# decription:   
#                   Confirmed crash on: WI-V3.0.6.33251; WI-T4.0.0.1779
#                   Checked on: 3.0.6.33252; WI-T4.0.0.1782 - works fine.
#                
# tracker_id:   CORE-6254
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set term ^;
    create or alter trigger trg_tx_start on transaction start as
        declare tx int;
    begin
        execute statement ('select current_transaction from rdb$database') into tx;
    end
    ^
    set term ;^
    commit;

    set transaction;
    select sign(current_transaction) as s from rdb$database;
    commit; -- this raised AV
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    S                               1
"""

@pytest.mark.version('>=3.0.6')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

