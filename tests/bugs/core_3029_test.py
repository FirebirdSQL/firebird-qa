#coding:utf-8
#
# id:           bugs.core_3029
# title:        Bugcheck "Too many savepoints (287)" at rollback after exception at EXECUTE BLOCK with exception handler
# decription:   
# tracker_id:   CORE-3029
# min_versions: ['2.5.1']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = [('line.*', ''), ('col.*', '')]

init_script_1 = """create sequence test_gen;

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

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """set term !!;
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\Users\\win7\\Firebird_tests\\fbt-repository\\tmp\\bugs.core_3029.fdb, User: SYSDBA
SQL> SQL> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON>
          ID          DID          DEP          PID
============ ============ ============ ============
      <null>            2            4            3
      <null>            2            4            3
SQL> SQL> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> CON> SQL>
          ID          DID          DEP          PID
============ ============ ============ ============
      <null>            2            4            3
SQL> SQL>"""
expected_stderr_1 = """Statement failed, SQLSTATE = 23000
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

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

