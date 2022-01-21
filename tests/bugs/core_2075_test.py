#coding:utf-8

"""
ID:          issue-2510
ISSUE:       2510
TITLE:       Parts of RDB$DB_KEY of views may be inverted when using outer joins
DESCRIPTION:
JIRA:        CORE-2075
"""

import pytest
from firebird.qa import *

init_script = """create table t1 (n integer);
create table t2 (n integer);

insert into t1 values (1);
insert into t1 values (2);
insert into t1 values (3);
insert into t1 values (4);
insert into t1 values (5);
insert into t1 values (6);

insert into t2 values (2);
insert into t2 values (4);
insert into t2 values (5);
insert into t2 values (8);
commit;

create view v (t1, t2) as
  select t1.rdb$db_key, t2.rdb$db_key
    from t1
    full join t2
      on t2.n = t1.n;
"""

db = db_factory(init=init_script)

test_script = """select v.rdb$db_key, v.*
  from v;
"""

act = isql_act('db', test_script)

expected_stdout = """
DB_KEY                           T1               T2
================================ ================ ================
81000000010000008000000002000000 8000000002000000 8100000001000000
81000000020000008000000004000000 8000000004000000 8100000002000000
81000000030000008000000005000000 8000000005000000 8100000003000000
81000000040000000000000000000000 <null>           8100000004000000
00000000000000008000000001000000 8000000001000000 <null>
00000000000000008000000003000000 8000000003000000 <null>
00000000000000008000000006000000 8000000006000000 <null>

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

