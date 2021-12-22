#coding:utf-8
#
# id:           bugs.core_5858
# title:        Command 'REVOKE ALL ON ALL FROM <anyname>' lead server to crash
# decription:   
#                  Detected/confirmed bug on 4.0.0.1036.
#                  Works fine on 4.0.0.1040
#                
# tracker_id:   CORE-5858
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set wng off;
    set bail on;
    revoke all on all from any_name_here;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.execute()

