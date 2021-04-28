#coding:utf-8
#
# id:           functional.basic.db.09
# title:        Empty DB - RDB$FILTERS
# decription:   Check for correct content of RDB$FILTERS in empty database.
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.basic.db.db_09

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select * from RDB$FILTERS;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.execute()

