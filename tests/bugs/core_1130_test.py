#coding:utf-8

"""
ID:          issue-1552
ISSUE:       1552
TITLE:       Bad optimization -- <procedure> left join <subquery> (or <view>)
DESCRIPTION:
JIRA:        CORE-1130
FBTEST:      bugs.core_1130
"""

import pytest
from firebird.qa import *

init_script = """SET TERM ^;
create procedure p
  returns (r int)
as
begin
  r = 1;
  suspend;
end
^
SET TERM ;^
COMMIT;
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
select *
from p
  left join ( select rdb$relation_id from rdb$relations ) r
    on p.r = r.rdb$relation_id;

"""

act = isql_act('db', test_script)

expected_stdout = """PLAN JOIN (P NATURAL, R RDB$RELATIONS INDEX (RDB$INDEX_1))

           R RDB$RELATION_ID
============ ===============
           1               1

"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

