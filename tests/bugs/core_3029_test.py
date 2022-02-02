#coding:utf-8

"""
ID:          issue-3410
ISSUE:       3410
TITLE:       Bugcheck "Too many savepoints (287)" at rollback after exception at EXECUTE BLOCK with exception handler
DESCRIPTION:
JIRA:        CORE-3029
FBTEST:      bugs.core_3029
"""

import pytest
from firebird.qa import *

init_script = """create sequence test_gen;

recreate table test_row
(id int not null,
 did int not null,
 pid int not null,
 dep int not null
);
alter table test_row add constraint pk_test_row primary key(id);
create unique index ix_test_row1 on test_row(did, pid, dep);
commit;

insert into test_row(id, did, pid,dep) values(1, 2, 3, 4);
commit;
"""

db = db_factory(init=init_script)

test_script = """set term !!;
execute block returns(id int, did int, dep int, pid int)
as
declare variable xid int;
begin
  select id,did, pid,dep
    from test_row
   where id=(select min(id) from test_row)
    into :xid, :did, pid, :dep;

  while (1=1) do
  begin
    delete from test_row r where r.id = :xid;

    insert into test_row(id, did, dep, pid)
    values (gen_id(test_gen, 1), :did, :dep, :pid);

    suspend;

  when any do
    exception;
  end
end !!
rollback !!
create or alter procedure sp_test
  returns(id int, did int, dep int, pid int)
as
declare variable xid int;
begin
  select id,did, pid,dep
    from test_row
   where id=(select min(id) from test_row)
    into :xid, :did, pid, :dep;

  while (1=1) do
  begin
    delete from test_row r where r.id = :xid;

    insert into test_row(id, did, dep, pid)
    values (gen_id(test_gen, 1), :did, :dep, :pid);

    suspend;

  when any do
    exception;
  end
end !!
select * from sp_test !!
rollback !!
"""

act = isql_act('db', test_script, substitutions=[('line.*', ''), ('col.*', '')])

expected_stdout = """
          ID          DID          DEP          PID
============ ============ ============ ============
      <null>            2            4            3
      <null>            2            4            3

          ID          DID          DEP          PID
============ ============ ============ ============
      <null>            2            4            3
"""

expected_stderr = """Statement failed, SQLSTATE = 23000
attempt to store duplicate value (visible to active transactions) in unique index "IX_TEST_ROW1"
-Problematic key value is ("DID" = 2, "PID" = 3, "DEP" = 4)
-At block
-At block
Statement failed, SQLSTATE = 23000
attempt to store duplicate value (visible to active transactions) in unique index "IX_TEST_ROW1"
-Problematic key value is ("DID" = 2, "PID" = 3, "DEP" = 4)
-At procedure 'SP_TEST' line: 15, col: 5
-At procedure 'SP_TEST' line: 20, col: 12
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

