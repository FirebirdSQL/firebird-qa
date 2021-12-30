#coding:utf-8
#
# id:           bugs.core_4774
# title:        Table aliasing is unnecessary required when doing UPDATE ... RETURNING RDB$ pseudo-columns
# decription:   
#                   NB. After fix #6815 execution plan contains 'Local_Table' (FB 5.0+) for DML with RETURNING clauses:
#                       "When such a statement is executed, Firebird should execute the statement to completion
#                        and collect all requested data in a type of temporary table, once execution is complete,
#                        fetches are done against this temporary table"
#               
#                   See https://github.com/FirebirdSQL/firebird/issues/6815 for details:
# tracker_id:   CORE-4774
# min_versions: ['3.0']
# versions:     3.0, 5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

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

@pytest.mark.version('>=3.0,<5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 5.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
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

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    PLAN (T NATURAL)
    PLAN (Local_Table NATURAL)

    PLAN (T NATURAL)
    PLAN (Local_Table NATURAL)

    PLAN (T NATURAL)
    PLAN (Local_Table NATURAL)
"""

@pytest.mark.version('>=5.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout

