#coding:utf-8
#
# id:           bugs.core_6282
# title:        Change type of MON$ATTACHMENTS.MON$IDLE_TIMER and MON$STATEMENTS.MON$STATEMENT_TIMER to TIMESTAMP WITH TIME ZONE
# decription:   
#                   Checked on 4.0.0.1881.
#                
# tracker_id:   CORE-6282
# min_versions: []
# versions:     4.0.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0.0
# resources: None

substitutions_1 = [('^((?!(sqltype)).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set sqlda_display on;
    set list on;
    select a.mon$idle_timer, s.mon$statement_timer from mon$attachments a join mon$statements s using(mon$attachment_id) rows 0;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 32754 TIMESTAMP WITH TIME ZONE Nullable scale: 0 subtype: 0 len: 12
    02: sqltype: 32754 TIMESTAMP WITH TIME ZONE Nullable scale: 0 subtype: 0 len: 12
"""

@pytest.mark.version('>=4.0.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

