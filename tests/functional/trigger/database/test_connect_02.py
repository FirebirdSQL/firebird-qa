#coding:utf-8

"""
ID:          trigger.database.connect-02
TITLE:       Error handling in trigger on database connect
DESCRIPTION:
  This test verifies the proper error handling. Uncaught exceptions in trigger roll back
  the transaction, disconnect the attachment and are returned to the client.
FBTEST:      functional.trigger.database.connect_02
"""

import pytest
from firebird.qa import *

init_script = """create table LOG (ID integer, MSG varchar(100));
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

db = db_factory(init=init_script)

act = python_act('db', substitutions=[('line:.*', '')])

expected_stdout = """Error while connecting to database:
- SQLCODE: -836
- exception 1
- CONNECTERROR
- Exception in ON CONNECT trigger
- At trigger 'ONCONNECT' line: 5, col: 29
-836
335544517
"""

@pytest.mark.skip('FIXME: Not IMPLEMENTED')
@pytest.mark.version('>=3.0')
def test_1(act: Action):
    pytest.fail("Not IMPLEMENTED")

# Original python code for this test:
# -----------------------------------
# try:
#   con = kdb.connect(dsn=dsn.encode(),user=user_name.encode(),password=user_password.encode(),role='TEST')
# except Exception,e:
#   for msg in e: print (msg)
# -----------------------------------
