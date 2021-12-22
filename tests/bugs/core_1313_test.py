#coding:utf-8
#
# id:           bugs.core_1313
# title:        RDB$DB_KEY not supported in derived tables and merge command
# decription:   
# tracker_id:   CORE-1313
# min_versions: []
# versions:     2.5
# qmid:         bugs.core_1313

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('=', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table t (c1 integer);
    commit;

    insert into t values (1);
    insert into t values (2);
    insert into t values (3);

    commit;
      
    select 'point-1' msg, t1.*
    from t t1
    right join (select t.rdb$db_key as dbkey from t) t2 on t2.dbkey = t1.rdb$db_key;

    merge into t t1
    using (select t.rdb$db_key as dbkey from t) t2
    on t2.dbkey = t1.rdb$db_key
    when not matched then insert values (null);

    select 'point-2' msg, t.* from t;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG     C1
    point-1  1
    point-1  2
    point-1  3

    MSG     C1
    point-2  1
    point-2  2
    point-2  3
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

