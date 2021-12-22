#coding:utf-8
#
# id:           bugs.core_4774
# title:        Table aliasing is unnecessary required when doing UPDATE ... RETURNING RDB$ pseudo-columns
# decription:   
# tracker_id:   CORE-4774
# min_versions: ['3.0']
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
    recreate table t(id int, x int);
    commit;
    insert into t values(1, 100);
    commit;
    set planonly;
    insert into t(id, x) values(2, 200) returning rdb$db_key;
    delete from t where id=1 returning rdb$db_key;
    update t set x=-x where id=2 returning rdb$db_key;
    update t set x=-x where id=2 returning rdb$record_version; 
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (T NATURAL)
    PLAN (T NATURAL)
    PLAN (T NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

