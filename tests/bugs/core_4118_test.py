#coding:utf-8

"""
ID:          issue-4446
ISSUE:       4446
TITLE:       Expression index may be not used for derived fields or view fields
DESCRIPTION:
JIRA:        CORE-4118
"""

import pytest
from firebird.qa import *

init_script = """create table t (id int, d timestamp);
create index itd on t computed (cast(d as date));
COMMIT;
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
select * from t where cast(d as date) = current_date;
select * from (select id, cast(d as date) as d from t) where d = current_date;
"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN (T INDEX (ITD))
PLAN (T INDEX (ITD))
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

