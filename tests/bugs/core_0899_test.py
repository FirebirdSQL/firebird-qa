#coding:utf-8

"""
ID:          issue-1296
ISSUE:       1296
TITLE:       Problems with explicit cursors in unwanted states
DESCRIPTION:
JIRA:        CORE-899
FBTEST:      bugs.core_0899
"""

import pytest
from firebird.qa import *

init_script = """create table T (ID integer, TXT varchar(30));
commit;

insert into T values (1,'Text description');
commit;

set term ^;

create procedure SP_OK returns (ID integer, TXT varchar(30))
as
  declare C cursor for ( select ID, TXT from T );
begin
  open C;
  while (1 = 1) do
  begin
    fetch C into :ID, :TXT;
    if (ROW_COUNT = 0) then
      leave;
    update T set TXT = 'OK' where current of C;
    suspend;
  end
  close C;
end ^

create procedure SP_CLOSED returns (ID integer, TXT varchar(30))
as
  declare C cursor for ( select ID, TXT from T );
begin
  open C;
  while (1 = 1) do
  begin
    fetch C into :ID, :TXT;
    if (ROW_COUNT = 0) then
      leave;
    suspend;
  end
  close C;
  update T set TXT = 'SP_CLOSED' where current of C;
end ^

create procedure SP_NOTOPEN returns (ID integer, TXT varchar(30))
as
  declare C cursor for ( select ID, TXT from T );
begin
  update T set TXT = 'SP_NOTOPEN' where current of C;
  open C;
  while (1 = 1) do
  begin
    fetch C into :ID, :TXT;
    if (ROW_COUNT = 0) then
      leave;
    suspend;
  end
  close C;
end ^

create procedure SP_FETCHED returns (ID integer, TXT varchar(30))
as
  declare C cursor for ( select ID, TXT from T );
begin
  open C;
  while (1 = 1) do
  begin
    fetch C into :ID, :TXT;
    if (ROW_COUNT = 0) then
      leave;
    suspend;
  end
  update T set TXT = 'SP_FETCHED' where current of C;
  close C;
end ^

set term ; ^

commit;
"""

db = db_factory(init=init_script)

test_script = """select * from SP_OK;
select * from SP_CLOSED;
select * from SP_NOTOPEN;
select * from SP_FETCHED;

"""

act = isql_act('db', test_script,
               substitutions=[('line:\\s[0-9]+,', 'line: x'), ('col:\\s[0-9]+', 'col: y')])

expected_stdout = """
          ID TXT
============ ==============================
           1 Text description


          ID TXT
============ ==============================
           1 OK

          ID TXT
============ ==============================

          ID TXT
============ ==============================
           1 OK
"""

expected_stderr = """Statement failed, SQLSTATE = 22000
no current record for fetch operation
-At procedure 'SP_CLOSED' line: 14, col: 3
Statement failed, SQLSTATE = 22000
no current record for fetch operation
-At procedure 'SP_NOTOPEN' line: 5, col: 3
Statement failed, SQLSTATE = 22000
no current record for fetch operation
-At procedure 'SP_FETCHED' line: 13, col: 3
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

