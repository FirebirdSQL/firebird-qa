#coding:utf-8
#
# id:           bugs.core_0908
# title:        Garbage in plan output of complex statement
# decription:   This is unfortunate case. The fix for 2.1 went through several "adjustments" and we've get lost in changes. The result is that this was not properly fixed in 2.1 line (server doesn't crash, but don't returns the truncated plan as supposed either). Now when 2.1 line is at 2.1.3 we can hope for proper fix in 2.1.4. It should work as intended in 2.5 line.
# tracker_id:   CORE-908
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_908

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """set term ^;

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

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """set plan on;
select * from big_plan ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN (BIG_PLAN NATURAL)
X
============
1
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

