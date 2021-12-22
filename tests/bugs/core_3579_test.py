#coding:utf-8
#
# id:           bugs.core_3579
# title:        Can not drop table when computed field depends on later created another field
# decription:   
# tracker_id:   CORE-3579
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core3579.fbk', init=init_script_1)

test_script_1 = """
    drop table Test; 
    show table;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
   There are no tables in this database
"""

@pytest.mark.version('>=2.5.2')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

