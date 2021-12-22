#coding:utf-8
#
# id:           bugs.core_1334
# title:        Joins with NULL RDB$DB_KEY crash the server
# decription:   
# tracker_id:   CORE-1334
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1334

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """create table t1 (id integer primary key);
create table t2 (id integer references t1);
COMMIT;
insert into t1 values (1);
insert into t1 values (2);
insert into t2 values (2);
COMMIT;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select *
  from t1
  left join t2
    on (t2.id = t1.id)
  left join t2 t3
    on (t3.rdb$db_key = t2.rdb$db_key);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          ID           ID           ID
============ ============ ============
           1       <null>       <null>
           2            2            2

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

