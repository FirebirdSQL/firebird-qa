#coding:utf-8

"""
ID:          issue-2489
ISSUE:       2489
TITLE:       Computed expressions may be optimized badly if used inside the RETURNING clause of the INSERT statement
DESCRIPTION:
JIRA:        CORE-2053
"""

import pytest
from firebird.qa import *

init_script = """create table t1 (col1 int);
create index i1 on t1 (col1);
commit;
insert into t1 (col1) values (1);
commit;
create table t2 (col2 int);
commit;
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
insert into t2 (col2) values (1) returning case when exists (select 1 from t1 where col1 = col2) then 1 else 0 end;
commit;"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN (T1 INDEX (I1))

        CASE
============
           1

"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

