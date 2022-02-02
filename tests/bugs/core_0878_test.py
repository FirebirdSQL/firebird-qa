#coding:utf-8

"""
ID:          issue-1271
ISSUE:       1271
TITLE:       Problem when dropping column that is a primary key
DESCRIPTION:
JIRA:        CORE-878
FBTEST:      bugs.core_0878
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """create table pk1 (i1 integer not null, i2 integer);
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

act = isql_act('db', test_script)

expected_stdout = """I1                              INTEGER Not Null
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

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

