#coding:utf-8

"""
ID:          issue-3367
ISSUE:       3367
TITLE:       The new 2.5 feature to alter COMPUTED columns doesn't handle dependencies well
DESCRIPTION:
JIRA:        CORE-2985
FBTEST:      bugs.core_2985
"""

import pytest
from firebird.qa import *

init_script = """create table test (id numeric, f1 varchar(20));
create table test1(id1 numeric, ff computed((select f1 from test where id=id1)));
commit;
"""

db = db_factory(init=init_script)

test_script = """show table test1;
alter table test1 alter ff computed(cast(null as varchar(20)));
drop table test;
commit;
show table test1;
"""

act = isql_act('db', test_script)

expected_stdout = """ID1                             NUMERIC(9, 0) Nullable
FF                              Computed by: ((select f1 from test where id=id1))
ID1                             NUMERIC(9, 0) Nullable
FF                              Computed by: (cast(null as varchar(20)))
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

