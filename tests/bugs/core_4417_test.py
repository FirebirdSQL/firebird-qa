#coding:utf-8
#
# id:           bugs.core_4417
# title:        gbak: cannot commit index ; primary key with german umlaut
# decription:   Test verifies only ability to restore database w/o errors.
# tracker_id:   CORE-4417
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core4417-ods-11_2.fbk', init=init_script_1)

test_script_1 = """
    -- Confirmed crash of restoring on WI-V2.5.2.26540: message about abnnormal program termination appeared.
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.execute()

