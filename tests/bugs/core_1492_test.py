#coding:utf-8
#
# id:           bugs.core_1492
# title:        BLOB isn't compatible with [VAR]CHAR in COALESCE
# decription:   
# tracker_id:   CORE-1492
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1492

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = [('B_BLOB.*', 'B_BLOB')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table t (id int primary key, b blob sub_type text );
    commit;

    insert into t(id, b) values (1, NULL);
    insert into t(id, b) values (2, 'QWER');
    commit;

    set list on;
    select coalesce(b, '') as b_blob
    from t
    order by id;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    B_BLOB                          0:1
    B_BLOB                          82:1e0
    QWER
"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

