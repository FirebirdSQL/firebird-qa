#coding:utf-8
#
# id:           bugs.core_6033
# title:        SUBSTRING(CURRENT_TIMESTAMP) does not work
# decription:   
#                   Confirmed bug on WI-T4.0.0.1457, got:
#                   ===
#                     Statement failed, SQLSTATE = 22001
#                     arithmetic exception, numeric overflow, or string truncation
#                     -string right truncation
#                     -expected length 34, actual 38
#                   ===
#                   Checked on 4.0.0.1479: OK, 1.299s.
#                
# tracker_id:   CORE-6033
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
        declare c varchar(100);
    begin
        c = substring(current_timestamp from 1);
    end
    ^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.execute()

