#coding:utf-8

"""
ID:          issue-4708
ISSUE:       4708
TITLE:       Report more details for "object in use" errors
DESCRIPTION:
NOTES:
[22.11.2021] pcisar
  This test requires READ_COMMITTED_NO_RECORD_VERSION transaction to work, which
  requires ReadConsistency disabled in FB 4. However, it does not work as expected
  because all drop commands pass without exception even with ReadConsistency disabled.
  The same happens under 3.0.8 (no errors raised).
JIRA:        CORE-4386
FBTEST:      bugs.core_4386
"""

import pytest
from firebird.qa import *
from firebird.driver import tpb, Isolation

db = db_factory()

act = python_act('db')

ddl_script = """
set bail on;
create or alter procedure sp_worker as begin end;
create or alter procedure sp_test as begin end;
create or alter view v_test as select 1 x from rdb$database;
commit;

recreate table test1(id int,x int);
recreate table test2(id int,x int);
commit;

create index test1_id on test1(id);
commit;
create descending index test2_id_x_desc on test2(id,x);
commit;

create or alter view v_test as select id,x from test1 where id between 15 and 30;
commit;

set term ^;
create or alter procedure sp_worker(a_id int) returns(x int) as
begin
  for
      execute statement ('select v.x from v_test v where v.id = ? and exists(select * from test2 b where b.id = v.id)') (:a_id)
      into x
  do
      suspend;
end
^
create or alter procedure sp_test(a_id int) returns(x int) as
begin
  for
      execute statement ('select x from sp_worker(?)') (:a_id)
      into x
  do
      suspend;
end
^
set term ;^
commit;

insert into test1 values(11,111);
insert into test1 values(21,222);
insert into test1 values(31,333);
insert into test1 values(41,444);
commit;

insert into test2 select * from test1;
commit;
"""

expected_stdout = """
    Error while commiting transaction:
    - SQLCODE: -901
    - lock conflict on no wait transaction
    - unsuccessful metadata update
    - object PROCEDURE "SP_TEST" is in use
    335544345

    Error while commiting transaction:
    - SQLCODE: -901
    - lock conflict on no wait transaction
    - unsuccessful metadata update
    - object PROCEDURE "SP_WORKER" is in use
    335544345

    Error while commiting transaction:
    - SQLCODE: -901
    - lock conflict on no wait transaction
    - unsuccessful metadata update
    - object VIEW "V_TEST" is in use
    335544345

    Error while commiting transaction:
    - SQLCODE: -901
    - lock conflict on no wait transaction
    - unsuccessful metadata update
    - object TABLE "TEST2" is in use
    335544345

    Error while commiting transaction:
    - SQLCODE: -901
    - lock conflict on no wait transaction
    - unsuccessful metadata update
    - object INDEX "TEST1_ID" is in use
    335544345

    Error while commiting transaction:
    - SQLCODE: -901
    - lock conflict on no wait transaction
    - unsuccessful metadata update
    - object INDEX "TEST2_ID_X_DESC" is in use
    335544345
"""

@pytest.mark.skip("FIXME: see notes")
@pytest.mark.version('>=3.0.6')
def test_1(act: Action, capsys):
    act.isql(switches=[], input=ddl_script)
    #
    custom_tpb = tpb(isolation=Isolation.READ_COMMITTED_NO_RECORD_VERSION, lock_timeout=0)
    with act.db.connect() as con:
        cur1 = con.cursor()
        cur1.execute('select x from sp_test(21)').fetchall()
        drop_commands = ['drop procedure sp_test',
                         'drop procedure sp_worker',
                         'drop view v_test',
                         'drop table test2',
                         'drop index test1_id',
                         'drop index test2_id_x_desc']
        for cmd in drop_commands:
            with act.db.connect() as con2:
                tx = con2.transaction_manager(custom_tpb)
                tx.begin()
                cur2 = tx.cursor()
                try:
                    cur2.execute(cmd)
                except Exception as exc:
                    print(exc)
    #
    act.reset()
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
