#coding:utf-8
#
# id:           functional.domain.create.54
# title:        Use of domains for Trigger/SP variable definition
# decription:   Allow domains to be applied to variables and in/out
#               parameters within a trigger or SP
# tracker_id:   CORE-660
# min_versions: []
# versions:     2.1
# qmid:         functional.domain.create.create_domain_54

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """create domain d as integer;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """set term !!;
create procedure sp (i type of d) returns (o type of d)
as
  declare variable v type of d;
begin
  v = cast(v as type of d);
end!!
commit!!
set term ;!!
show procedure sp;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Procedure text:
=============================================================================
  declare variable v type of d;
begin
  v = cast(v as type of d);
end
=============================================================================
Parameters:
I                                 INPUT (TYPE OF D) INTEGER
O                                 OUTPUT (TYPE OF D) INTEGER"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

