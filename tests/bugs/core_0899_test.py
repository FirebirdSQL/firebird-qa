#coding:utf-8
#
# id:           bugs.core_0899
# title:        Problems with explicit cursors in unwanted states
# decription:   
# tracker_id:   CORE-899
# min_versions: []
# versions:     2.5.0
# qmid:         bugs.core_899-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = [('line:\\s[0-9]+,', 'line: x'), ('col:\\s[0-9]+', 'col: y')]

init_script_1 = """create table T (ID integer, TXT varchar(30));
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

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select * from SP_OK;
select * from SP_CLOSED;
select * from SP_NOTOPEN;
select * from SP_FETCHED;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
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
expected_stderr_1 = """Statement failed, SQLSTATE = 22000
no current record for fetch operation
-At procedure 'SP_CLOSED' line: 14, col: 3
Statement failed, SQLSTATE = 22000
no current record for fetch operation
-At procedure 'SP_NOTOPEN' line: 5, col: 3
Statement failed, SQLSTATE = 22000
no current record for fetch operation
-At procedure 'SP_FETCHED' line: 13, col: 3
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

