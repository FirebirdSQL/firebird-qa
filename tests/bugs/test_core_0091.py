#coding:utf-8
#
# id:           bugs.core_91
# title:        Recreate and self-referencing indexes
# decription:   
# tracker_id:   CORE-91
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_91

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """recreate table t2 (
    i integer not null primary key,
    p integer references t2(i) on delete set null
 );
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select * from t2;
insert into t2 values (1, null);
delete from t2 where i=1;
commit;

recreate table t2 (
    i integer not null primary key,
    p integer references t2(i) on delete set null
 );
commit;
select * from t2;
insert into t2 values (1, null);
delete from t2 where i=1;
commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1')
def test_core_91_1(act_1: Action):
    act_1.execute()

