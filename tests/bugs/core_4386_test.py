#coding:utf-8
#
# id:           bugs.core_4386
# title:        Report more details for "object in use" errors
# decription:
#                   Checked on 3.0.6.33242 (intermediate build) after discuss with dimitr.
#
# tracker_id:   CORE-4386
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action
from firebird.driver import TPB, Isolation

# version: 3.0.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import subprocess
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_conn.close()
#
#  CUSTOM_TX_PARAMS = ( [ fdb.isc_tpb_read_committed, fdb.isc_tpb_no_rec_version, fdb.isc_tpb_nowait ] )
#
#  sql_ddl='''
#      set bail on;
#      create or alter procedure sp_worker as begin end;
#      create or alter procedure sp_test as begin end;
#      create or alter view v_test as select 1 x from rdb$database;
#      commit;
#
#      recreate table test1(id int,x int);
#      recreate table test2(id int,x int);
#      commit;
#
#      create index test1_id on test1(id);
#      commit;
#      create descending index test2_id_x_desc on test2(id,x);
#      commit;
#
#      create or alter view v_test as select id,x from test1 where id between 15 and 30;
#      commit;
#
#      set term ^;
#      create or alter procedure sp_worker(a_id int) returns(x int) as
#      begin
#        for
#            execute statement ('select v.x from v_test v where v.id = ? and exists(select * from test2 b where b.id = v.id)') (:a_id)
#            into x
#        do
#            suspend;
#      end
#      ^
#      create or alter procedure sp_test(a_id int) returns(x int) as
#      begin
#        for
#            execute statement ('select x from sp_worker(?)') (:a_id)
#            into x
#        do
#            suspend;
#      end
#      ^
#      set term ;^
#      commit;
#
#      insert into test1 values(11,111);
#      insert into test1 values(21,222);
#      insert into test1 values(31,333);
#      insert into test1 values(41,444);
#      commit;
#
#      insert into test2 select * from test1;
#      commit;
#  '''
#
#  runProgram('isql', [ dsn ], sql_ddl)
#
#  con1=fdb.connect(dsn = dsn)
#  cur1=con1.cursor()
#  cur1.execute('select x from sp_test(21)')
#  for r in cur1:
#      pass
#
#  drop_commands = [
#      'drop procedure sp_test',
#      'drop procedure sp_worker',
#      'drop view v_test',
#      'drop table test2',
#      'drop index test1_id',
#      'drop index test2_id_x_desc'
#  ]
#
#  for i,c in enumerate(drop_commands):
#      con2=fdb.connect(dsn = dsn)
#      tx = con2.trans( default_tpb = CUSTOM_TX_PARAMS )
#      #############################################
#      # READ COMMITTED | NO_RECORD_VERSION | NOWAIT
#      #############################################
#      tx.begin()
#      cur2=tx.cursor()
#
#      try:
#          cur2.execute( c )
#          tx.commit()
#      except Exception as e:
#          print(e[0])
#          print(e[2])
#      finally:
#          cur2.close()
#          con2.close()
#
#  cur1.close()
#  con1.close()
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
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

@pytest.mark.version('>=3.0.6')
def test_1(act_1: Action, capsys):
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
    act_1.isql(switches=[], input=ddl_script)
    #
    tpb = TPB(isolation=Isolation.READ_COMMITTED_NO_RECORD_VERSION, lock_timeout=0).get_buffer()
    with act_1.db.connect() as con:
        cur1 = con.cursor()
        cur1.execute('select x from sp_test(21)').fetchall()
        drop_commands = ['drop procedure sp_test',
                         'drop procedure sp_worker',
                         'drop view v_test',
                         'drop table test2',
                         'drop index test1_id',
                         'drop index test2_id_x_desc']
        for cmd in drop_commands:
            with act_1.db.connect() as con2:
                tx = con2.transaction_manager(default_tpb=tpb)
                tx.begin()
                cur2 = tx.cursor()
                try:
                    cur2.execute(cmd)
                except Exception as exc:
                    print(exc)
    #
    act_1.reset()
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    # [pcisar] 22.11.2021
    # This test requires READ_COMMITTED_NO_RECORD_VERSION transaction to work, which
    # requires ReadConsistency disabled in FB 4. However, it does not work as expected
    # because all drop commands pass without exception even with ReadConsistency disabled.
    # Not yet tested with FB3. I also expect it FAIL due to exception differences in FDB
    # and new driver (this will be fixed once we make it to raise "object in use" exception)
    assert act_1.clean_stdout == act_1.clean_expected_stdout
