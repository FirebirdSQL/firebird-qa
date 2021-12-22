#coding:utf-8
#
# id:           bugs.core_3282
# title:        EXECUTE STATEMENT parses the SQL text using wrong charset
# decription:   
# tracker_id:   CORE-3282
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core3282.fbk', init=init_script_1)

test_script_1 = """
    execute procedure TESTSP; -- 2.5.0 only: get "Malformed string" when connect with cset=utf8, confirmed 26.02.2015
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.execute()

