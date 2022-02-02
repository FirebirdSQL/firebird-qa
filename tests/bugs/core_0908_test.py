#coding:utf-8

"""
ID:          issue-1307
ISSUE:       1307
TITLE:       Garbage in plan output of complex statement
DESCRIPTION:
  This is unfortunate case. The fix for 2.1 went through several "adjustments" and we've
  get lost in changes. The result is that this was not properly fixed in 2.1 line (server
  doesn't crash, but don't returns the truncated plan as supposed either). Now when 2.1
  line is at 2.1.3 we can hope for proper fix in 2.1.4. It should work as intended in 2.5 line.
JIRA:        CORE-908
FBTEST:      bugs.core_0908
"""

import pytest
from firebird.qa import *

init_script = """set term ^;

create procedure big_plan
  returns (x integer)
as
begin
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;

  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;

  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;

  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;

  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;

  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;

  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;

  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;

  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;

  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
  select 1 from rdb$database into :x;
/*  select 1 from rdb$relations into :x; */
  suspend;
end ^
set term ;^
"""

db = db_factory(init=init_script)

test_script = """set plan on;
select * from big_plan ;
"""

act = isql_act('db', test_script)

expected_stdout = """PLAN (BIG_PLAN NATURAL)
X
============
1
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

