#coding:utf-8
#
# id:           bugs.core_3959
# title:        Repeat Temporary Table access from ReadOnly Transaction and ReadWrite transaction causes Internal Firebird consistency check (cannot find record back version (291), file: vio.cpp line: 4905)
# decription:
#                  Bug in WI-V2.5.1.26351: execution of last line ('print( cur1a.fetchall() )') leads FB to crash, log:
#                  ===
#                        Access violation.
#                               The code attempted to access a virtual
#                               address without privilege to do so.
#                       This exception will cause the Firebird server
#                       to terminate abnormally.
#                  ===
#                  No problem in 2.5.7 and 3.0.x
#
# tracker_id:   CORE-3959
# min_versions: ['2.5.7']
# versions:     2.5.7
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action
from firebird.driver import TPB, TraAccessMode, Isolation

# version: 2.5.7
# resources: None

substitutions_1 = []

init_script_1 = """
    create or alter procedure fu_x1 as begin end;
    create or alter procedure save_x1 as begin end;
    commit;

    recreate global temporary table x1 (
        id integer,
        name varchar(10)
    ) on commit preserve rows;


    set term ^;
    alter procedure fu_x1 returns (
        sid integer,
        sname varchar(10)) as
    begin
        delete from x1;

        insert into x1 values (1,'1');
        insert into x1 values (2,'2');
        insert into x1 values (3,'3');
        insert into x1 values (4,'4');
        insert into x1 values (5,'5');

        for
            select x1.id, x1.name
        from x1
            into sid, sname
        do
            suspend;
    end
    ^
    alter procedure save_x1 (
        pid integer,
        pname varchar(10))
    as
    begin
        update x1 set name = :pname
        where x1.id = :pid;
        if (row_count = 0) then
            insert into x1 values( :pid, :pname);
    end
    ^
    set term ;^
    commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import fdb
#  os.environ["ISC_USER"] = 'SYSDBA'
#  os.environ["ISC_PASSWORD"] = 'masterkey'
#
#  db_conn.close()
#
#  txparam1 = ( [ fdb.isc_tpb_read_committed, fdb.isc_tpb_rec_version, fdb.isc_tpb_nowait, fdb.isc_tpb_read ] )
#  txparam2 = ( [ fdb.isc_tpb_read_committed, fdb.isc_tpb_rec_version, fdb.isc_tpb_nowait ] )
#
#  con1 = fdb.connect(dsn=dsn)
#  #print(con1.firebird_version)
#
#  print('step-1')
#  tx1a=con1.trans( default_tpb = txparam1 )
#  print('step-2')
#  cur1a = tx1a.cursor()
#
#  print('step-3')
#  cur1a.execute("select sid, sname from FU_X1")
#  print('step-4')
#
#  tx1b=con1.trans( default_tpb = txparam2 )
#
#  print('step-5')
#  cur1b = tx1b.cursor()
#  print('step-6')
#  cur1b.callproc("save_x1", ('2', 'foo'))
#
#  print('step-7')
#  tx1b.commit()
#
#  #cur1b.callproc("save_x1", (3, 'bar'))
#  #tx1b.commit()
#
#  print('step-8')
#  cur1a.execute("select sid, sname from FU_X1")
#  print('step-9')
#  print( cur1a.fetchall() )
#
#  '''
#     Output in 2.5.1:
#        step-1
#        ...
#        step-9
#        Traceback (most recent call last):
#          File "c3959-run.py", line 42, in <module>
#            print( cur1a.fetchall() )
#          File "C:\\Python27\\lib\\site-packages
#  db
#  bcore.py", line 3677, in fetchall
#            return [row for row in self]
#          File "C:\\Python27\\lib\\site-packages
#  db
#  bcore.py", line 3440, in next
#            row = self.fetchone()
#          File "C:\\Python27\\lib\\site-packages
#  db
#  bcore.py", line 3637, in fetchone
#            return self._ps._fetchone()
#          File "C:\\Python27\\lib\\site-packages
#  db
#  bcore.py", line 3325, in _fetchone
#            "Cursor.fetchone:")
#        fdb.fbcore.DatabaseError: ('Cursor.fetchone:
#  - SQLCODE: -902
#  - Unable to complete network request to host "localhost".
#  - Error reading data from the connection.', -902, 335544721)
#  '''
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=2.5.7')
def test_1(act_1: Action):
    with act_1.db.connect() as con:
        txparam_read = TPB(isolation=Isolation.READ_COMMITTED_RECORD_VERSION, lock_timeout=0,
                           access_mode=TraAccessMode.READ).get_buffer()
        txparam_write = TPB(isolation=Isolation.READ_COMMITTED_RECORD_VERSION, lock_timeout=0).get_buffer()

        tx_read = con.transaction_manager(txparam_read)
        cur_read = tx_read.cursor()
        cur_read.execute("select sid, sname from FU_X1")

        tx_write = con.transaction_manager(txparam_write)
        cur_write = tx_write.cursor()
        cur_write.callproc("save_x1", ['2', 'foo'])
        tx_write.commit()

        cur_read.execute("select sid, sname from FU_X1")
        cur_read.fetchall() # If this does not raises an exception, the test passes
