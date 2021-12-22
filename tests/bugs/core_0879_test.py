#coding:utf-8
#
# id:           bugs.core_0879
# title:        Dependencies are not cleared when creation of expression index fails
# decription:   
# tracker_id:   CORE-879
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table tab ( a varchar(10000) );
    commit;
    create index ix on tab computed by (upper(a));
    drop table tab;
    commit;
    show table tab;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -key size exceeds implementation restriction for index "IX"
    There is no table TAB in this database
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

