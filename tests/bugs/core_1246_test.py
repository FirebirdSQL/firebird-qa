#coding:utf-8

"""
ID:          issue-1670
ISSUE:       1670
TITLE:       Incorrect column values with outer joins and derived tables
DESCRIPTION:
JIRA:        CORE-1246
FBTEST:      bugs.core_1246
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE T1 (N INTEGER);
CREATE TABLE T2 (N INTEGER);

insert into t1 values (1);
insert into t1 values (2);
insert into t2 values (2);
commit;"""

db = db_factory(init=init_script)

test_script = """select *
    from (select 1 n from rdb$database) t1
    full join (select 2 n from rdb$database) t2
        on (t2.n = t1.n)
;

"""

act = isql_act('db', test_script)

expected_stdout = """
           N            N
============ ============
      <null>            2
           1       <null>

"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

