#coding:utf-8

"""
ID:          issue-1837
ISSUE:       1837
TITLE:       Wrong current timestamp evaluation for selectable procedures
DESCRIPTION:
  In our implementation, CURRENT_DATE/TIME[STAMP] values are evaluated at the request
  (aka SQL statement) start time and are permanent for the duration of that request.
  This rule includes the nested calls (procedures and triggers) as well, i.e. they inherit
  the parent's timestamp, thus providing the stable date-time value for the entire call stack.
  However, this rule is broken for selectable procedures that evaluate current date-time
  values at every invocation.
JIRA:        CORE-1419
"""

import pytest
from firebird.qa import *

init_script = """set term ^;

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

db = db_factory(init=init_script)

test_script = """SELECT COUNT(*)
FROM ts2
WHERE cast(ts_self as varchar(50))=cast(ts_execute as varchar(50))
AND cast(ts_self as varchar(50))=cast(ts_select as varchar(50))
;

"""

act = isql_act('db', test_script)

expected_stdout = """
                COUNT
=====================
                    2

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

