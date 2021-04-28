#coding:utf-8
#
# id:           bugs.core_4822
# title:        MERGE JOIN cannot be used for DBKEY based expressions
# decription:   Test is related ONLY to versions 2.x. Block for 3.0 intentionally left EMPTY.
# tracker_id:   CORE-4822
# min_versions: ['2.5.5']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    --- SKIP any test for 3.0 for this ticket ---
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.execute()

