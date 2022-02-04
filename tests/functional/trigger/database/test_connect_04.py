#coding:utf-8

"""
ID:          trigger.database.connect-04
TITLE:       Error handling in trigger on database connect - multiple triggers.
DESCRIPTION:
  This test verifies the proper error handling. Uncaught exceptions in trigger roll back
  the transaction, disconnect the attachment and are returned to the client. Because this
  test is implemented in Python, our test support class creates a database connection for
  our test code (db_conn) that attach to the database without role specification. We verify
  that this connection was properly logged for convenience.
FBTEST:      functional.trigger.database.connect_04
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

create trigger ONCONNECT_1 on connect position 0
as
begin
  insert into LOG (MSG) values ('Connect T1 as ' || current_role);
end ^

create trigger ONCONNECT_2 on connect position 0
as
begin
  insert into LOG (MSG) values ('Connect T2 as ' || current_role);
  if (current_role ='TEST') then
      exception CONNECTERROR;
end ^

create trigger ONCONNECT_3 on connect position 20
as
begin
  insert into LOG (MSG) values ('Connect T3 as ' || current_role);
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
- At trigger 'ONCONNECT_2' line: 5, col: 29
-836
335544517
ID          MSG
----------- ----------------------------------------------------------------------------------------------------
1           Connect T1 as NONE
2           Connect T2 as NONE
3           Connect T3 as NONE
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
#
# c = db_conn.cursor()
# c.execute('select * from LOG')
# printData(c)
# -----------------------------------
