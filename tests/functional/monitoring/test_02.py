#coding:utf-8
#
# id:           functional.monitoring.02
# title:        Monitoring: get data about active statements from current attachment (WHERE-filter: mon$statements.mon$state=1).
# decription:   
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.monitoring.monitoring_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('SQL_TEXT.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set width usr 31;
    set list on;
    select a.mon$user usr, s.mon$sql_text sql_text
    from mon$attachments a
        join mon$statements s on a.mon$attachment_id = s.mon$attachment_id
    where
        a.mon$attachment_id = current_connection
        and s.mon$state = 1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    USR                             SYSDBA                                                                                       
    SQL_TEXT                        0:1
    select a.mon$user usr, s.mon$sql_text sql_text
    from mon$attachments a
        join mon$statements s on a.mon$attachment_id = s.mon$attachment_id
    where
        a.mon$attachment_id = current_connection
        and s.mon$state = 1
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

