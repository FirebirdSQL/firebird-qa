#coding:utf-8
#
# id:           bugs.core_1142
# title:        Cannot alter generator's comment to the same value
# decription:   
# tracker_id:   CORE-1142
# min_versions: []
# versions:     2.0.2
# qmid:         bugs.core_1142

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.2
# resources: None

substitutions_1 = []

init_script_1 = """create generator T;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """comment on generator T is 'comment';
commit;
show comment on generator T;
comment on generator T is 'comment';
commit;
show comment on generator T;
comment on generator T is 'different comment';
commit;
show comment on generator T;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """COMMENT ON GENERATOR    T IS comment;
COMMENT ON GENERATOR    T IS comment;
COMMENT ON GENERATOR    T IS different comment;
"""

@pytest.mark.version('>=2.0.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

