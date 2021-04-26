#coding:utf-8
#
# id:           bugs.core_878
# title:        problem when dropping column that is a primary key
# decription:   
# tracker_id:   CORE-878
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_878

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """create table pk1 (i1 integer not null, i2 integer);
alter table pk1 add primary key (i1);
commit;
show table pk1;
alter table pk1 drop i1;
commit;

create table pk2 (i1 integer not null, i2 integer);
alter table pk2 add constraint pk2_pk primary key (i1);
commit;
show table pk2;
alter table pk2 drop i1;
commit;

create table pk3 (i1 integer not null primary key, i2 integer);
commit;
show table pk3;
alter table pk3 drop i1;
commit;

show table pk1;

show table pk2;

show table pk3;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """I1                              INTEGER Not Null
I2                              INTEGER Nullable
CONSTRAINT INTEG_2:
  Primary key (I1)
I1                              INTEGER Not Null
I2                              INTEGER Nullable
CONSTRAINT PK2_PK:
  Primary key (I1)
I1                              INTEGER Not Null
I2                              INTEGER Nullable
CONSTRAINT INTEG_5:
  Primary key (I1)
I2                              INTEGER Nullable
I2                              INTEGER Nullable
I2                              INTEGER Nullable
"""

@pytest.mark.version('>=2.1')
def test_core_878_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

