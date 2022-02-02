#coding:utf-8

"""
ID:          issue-5429
ISSUE:       5429
TITLE:       Suboptimal join order if one table has a selective predicate and MIN is calculated for the other one
DESCRIPTION:
JIRA:        CORE-5146
FBTEST:      bugs.core_5146
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- Confirmed:
    -- effective plan on: V3.0.0.32435, T4.0.0.113
    -- ineffect. plan on: V3.0.0.32378, T4.0.0.98

    recreate table houritems(houritemid int, projectid int); -- hi
    recreate table dihourentries(houritemid int, datevalue int); -- he

    create index hi_itemid on houritems(houritemid);
    create index hi_projid on houritems(projectid);
    create index he_itemid on dihourentries(houritemid);
    create index he_datevl on dihourentries(datevalue);

    set planonly;

    select min(he.datevalue)
    from houritems hi inner join dihourentries he on hi.houritemid = he.houritemid
    where hi.projectid = ?;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN JOIN (HI INDEX (HI_PROJID), HE INDEX (HE_ITEMID))
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

