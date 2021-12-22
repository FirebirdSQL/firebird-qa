#coding:utf-8
#
# id:           bugs.core_1436
# title:        Outer joins don't work properly with the MON$ tables
# decription:   
# tracker_id:   CORE-1436
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1436

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select db.MON$FORCED_WRITES fw
    from mon$attachments att
    left join mon$database db on db.mon$creation_date = att.mon$timestamp
    rows 1;
    -- select db.mon$database_name
    --  from mon$attachments att
    --  left join mon$database db on db.mon$creation_date = att.mon$timestamp;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    FW                              <null>
"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

