#coding:utf-8
#
# id:           bugs.core_1130
# title:        Bad optimization -- <procedure> left join <subquery> (or <view>)
# decription:   
# tracker_id:   
# min_versions: []
# versions:     2.0.1
# qmid:         bugs.core_1130

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.1
# resources: None

substitutions_1 = []

init_script_1 = """SET TERM ^;
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

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
select *
from p
  left join ( select rdb$relation_id from rdb$relations ) r
    on p.r = r.rdb$relation_id;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN JOIN (P NATURAL, R RDB$RELATIONS INDEX (RDB$INDEX_1))

           R RDB$RELATION_ID
============ ===============
           1               1

"""

@pytest.mark.version('>=2.0.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

