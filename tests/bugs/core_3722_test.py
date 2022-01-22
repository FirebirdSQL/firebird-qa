#coding:utf-8

"""
ID:          issue-1397
ISSUE:       1397
TITLE:       IS NOT DISTINCT FROM NULL doesn't use index
DESCRIPTION:
JIRA:        CORE-3722
"""

import pytest
from firebird.qa import *

init_script = """create table t (a varchar(5));
create index t_a on t (a);
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
select * from t where a is null;
select * from t where a is not distinct from null;
select * from t where a is not distinct from null PLAN (T INDEX (T_A));
select * from t where a is not distinct from nullif('', '');
"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN (T INDEX (T_A))
PLAN (T INDEX (T_A))
PLAN (T INDEX (T_A))
PLAN (T INDEX (T_A))
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

