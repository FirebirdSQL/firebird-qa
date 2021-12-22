#coding:utf-8
#
# id:           bugs.core_3101
# title:        Cannot alter the domain after migrating from older versions
# decription:   
# tracker_id:   CORE-3101
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core3101-ods11.fbk', init=init_script_1)

test_script_1 = """
    show domain state;
    alter domain state set default 0;
    commit;
    show domain state;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    STATE                           SMALLINT Nullable
    STATE                           SMALLINT Nullable
                                    default 0
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

