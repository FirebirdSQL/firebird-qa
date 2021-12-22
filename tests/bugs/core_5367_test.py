#coding:utf-8
#
# id:           bugs.core_5367
# title:        Regression: (boolean) parameters as search condition no longer allowed
# decription:   
#                 Confirmed on WI-T4.0.0.397 before commit 04-oct-2016 17:52
#                 https://github.com/FirebirdSQL/firebird/commit/8a4b7e3b79a31dc7bf6e569e6cf673cf6899a475
#                 - got:
#                         Statement failed, SQLSTATE = 22000
#                         Dynamic SQL Error
#                         -SQL error code = -104
#                         -Invalid usage of boolean expression
#               
#                 Works fine since that commit (checked on LI-T4.0.0.397).
#                
# tracker_id:   CORE-5367
# min_versions: ['3.0.2']
# versions:     3.0.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.2
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test(id int,boo boolean);
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set sqlda_display on;
    set planonly;
    select * from test where ?;
    set planonly;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    INPUT message field count: 1
    01: sqltype: 32764 BOOLEAN scale: 0 subtype: 0 len: 1
      :  name:   alias:
      : table:   owner:

    PLAN (TEST NATURAL)

    OUTPUT message field count: 2
    01: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
      :  name: ID  alias: ID
      : table: TEST  owner: SYSDBA
    02: sqltype: 32764 BOOLEAN Nullable scale: 0 subtype: 0 len: 1
      :  name: BOO  alias: BOO
      : table: TEST  owner: SYSDBA
"""

@pytest.mark.version('>=3.0.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

