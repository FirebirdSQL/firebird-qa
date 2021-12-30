#coding:utf-8
#
# id:           functional.trigger.database.connect_02
# title:        Error handling in trigger on database connect
# decription:   This test verifies the proper error handling. Uncaught exceptions in trigger roll back the transaction, disconnect the attachment and are returned to the client.
# tracker_id:   CORE-745
# min_versions: []
# versions:     2.1
# qmid:         functional.trigger.database.connect_02

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.1
# resources: None

substitutions_1 = [('line:.*', '')]

init_script_1 = """create table LOG (ID integer, MSG varchar(100));
create generator LOGID;
create exception CONNECTERROR 'Exception in ON CONNECT trigger';
create role TEST;
grant TEST to PUBLIC;
set term ^;
create trigger LOG_BI for LOG active before insert position 0
as
begin
  if (new.ID is null) then
    new.ID = gen_id(LOGID,1);
end ^

create trigger ONCONNECT on connect position 0
as
begin
  insert into LOG (MSG) values ('Connect as ' || current_role);
  if (current_role ='TEST') then
      exception CONNECTERROR;
end ^

set term ;^

commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# try:
#    con = kdb.connect(dsn=dsn.encode(),user=user_name.encode(),password=user_password.encode(),role='TEST')
#  except Exception,e:
#    for msg in e: print (msg)
#---
act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """Error while connecting to database:
- SQLCODE: -836
- exception 1
- CONNECTERROR
- Exception in ON CONNECT trigger
- At trigger 'ONCONNECT' line: 5, col: 29
-836
335544517"""

@pytest.mark.version('>=2.1')
@pytest.mark.xfail
def test_1(act_1: Action):
    pytest.fail("Test not IMPLEMENTED")


