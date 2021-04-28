#coding:utf-8
#
# id:           bugs.core_1409
# title:        Support for autonomous transactions
# decription:   
# tracker_id:   CORE-1409
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create table log (
  msg varchar(60)
);
commit;
set term !;

create trigger t_conn on connect
as
begin
  if (current_user = 'SYSDBA') then
  begin
    in autonomous transaction
    do
    begin
      insert into log (msg) values ('SYSDBA connected');
    end
  end
end!

set term ;!
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select msg from log;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:btest2	mpugs.core_1409.fdb, User: SYSDBA
SQL>
MSG
============================================================
SYSDBA connected

SQL>"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

