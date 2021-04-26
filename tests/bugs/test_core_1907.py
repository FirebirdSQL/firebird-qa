#coding:utf-8
#
# id:           bugs.core_1907
# title:        Dropping and adding a domain constraint in the same transaction leaves incorrect dependencies
# decription:   
# tracker_id:   CORE-1907
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t1 (n integer);
create table t2 (n integer);

create domain d1 integer check (value = (select n from t1));
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """set autoddl off;

alter domain d1 drop constraint;
alter domain d1 add constraint check (value = (select n from t2));;
commit;

drop table t1; -- cannot drop - there are dependencies
commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.0')
def test_core_1907_1(act_1: Action):
    act_1.execute()

