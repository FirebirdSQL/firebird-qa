#coding:utf-8
#
# id:           bugs.core_1419
# title:        Wrong current timestamp evaluation for selectable procedures
# decription:   In our implementation, CURRENT_DATE/TIME[STAMP] values are evaluated at the request (aka SQL statement) start time and are permanent for the duration of that request. This rule includes the nested calls (procedures and triggers) as well, i.e. they inherit the parent's timestamp, thus providing the stable date-time value for the entire call stack. However, this rule is broken for selectable procedures that evaluate current date-time values at every invocation.
# tracker_id:   CORE-1419
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_1419

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """set term ^;

create procedure ts1 returns ( ts timestamp )
as
begin
  ts = current_timestamp;
  suspend;
end^

create procedure ts2 returns ( ts_self timestamp, ts_execute timestamp, ts_select timestamp )
as
  declare cnt int = 1000000;
begin
  ts_self = current_timestamp;
  execute procedure ts1 returning_values :ts_execute;
  select ts from ts1 into :ts_select;
  suspend;

  while (cnt > 0) do
    cnt = cnt - 1;

  ts_self = current_timestamp;
  execute procedure ts1 returning_values :ts_execute;
  select ts from ts1 into :ts_select;
  suspend;
end^

set term ;^

commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT COUNT(*)
FROM ts2
WHERE cast(ts_self as varchar(50))=cast(ts_execute as varchar(50))
AND cast(ts_self as varchar(50))=cast(ts_select as varchar(50))
;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                COUNT
=====================
                    2

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

