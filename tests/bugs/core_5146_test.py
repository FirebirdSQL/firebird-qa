#coding:utf-8
#
# id:           bugs.core_5146
# title:        Suboptimal join order if one table has a selective predicate and MIN is calculated for the other one
# decription:   
# tracker_id:   CORE-5146
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN JOIN (HI INDEX (HI_PROJID), HE INDEX (HE_ITEMID))
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

