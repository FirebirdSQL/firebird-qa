#coding:utf-8
#
# id:           functional.basic.db.17
# title:        Empty DB - RDB$LOG_FILES
# decription:   Check for correct content of RDB$LOG_FILES in empty database.
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.basic.db.db_17

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select * from RDB$LOG_FILES;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=1.0')
def test_17_1(act_1: Action):
    act_1.execute()

