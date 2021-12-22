#coding:utf-8
#
# id:           bugs.core_6397
# title:        Message length error with COALESCE and TIME/TIMESTAMP WITHOUT TIME ZONE and WITH TIME ZONE
# decription:   
#                  Test uses EXECUTE BLOCK with dummy variable to store reuslt (w/o suspend in order to prevent any output).
#                  EXECUTE STATEMENT must be used here for reproducing problem (no error with static PSQL code).
#               
#                  Confirmed bug on 4.0.0.2173.
#                  Checked on 4.0.0.2188 -- all fine.
#                
# tracker_id:   
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    execute block as
        declare dummy timestamp;
    begin
        execute statement 'select coalesce(localtimestamp, current_timestamp) from rdb$database' into dummy;
    end
    ^
    set term ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.execute()

