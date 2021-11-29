#coding:utf-8
#
# id:           bugs.core_5110
# title:        False PK\FK violation could be reported when attachment used isc_dpb_no_garbage_collect flag
# decription:
#                  Fix relates only such transactions that are in the state 'dead', see: https://sourceforge.net/p/firebird/code/62965
#                  This mean that such Tx should did sufficiently big changes _before_ inserting key into table with PK/UK.
#                  Number of these changes should force Tx-1 be rolled back via TIP rather than undo+commit.
#                  Simple experiment shows that threshold is near 80'000 rows being inserted into the table with single
#                  text field of length = 50 characters. This test inserts 120'000 rows for ensuring that rollback will be
#                  done via TIP.
#                  ===
#                  ::: NB :::
#                  Minimal version of 'fdb' driver should be 1.5.1 for this test can be run.
#                  ::::::::::
#                  Confirmed exception with PK/UK violation on WI-V3.0.0.32332 (11-feb-2016), 2.5.6.26970 (05-feb-2016):
#                  - SQLCODE: -803 ; - violation of PRIMARY or UNIQUE KEY constraint "TEST_ID_UNQ" on table "TEST"
#                  - Problematic key value is ("ID" = 1) ; -803 ; 335544665
#
#                  No such error on WI-T4.0.0.32371, WI-V2.5.6.26979.
#
# tracker_id:   CORE-5110
# min_versions: ['2.5.6']
# versions:     2.5.6
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action
from firebird.driver import DbWriteMode, TPB, Isolation

# version: 2.5.6
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test( id int, who varchar(5), constraint test_id_unq unique(id) using index test_id_unq );
    recreate table tbig( s varchar(50) );
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import fdb
#
#  db_conn.close()
#
#  # This reduces test running time from ~5" to ~4":
#  runProgram('gfix',[dsn,'-user',user_name,'-pas',user_password,'-w','async'])
#
#  # Specifying 'no_gc=1' requires fdb version >= 1.5.1, issued 19-feb-2016, see:
#  # http://sourceforge.net/p/firebird/code/62989
#  conn = fdb.connect(dsn=dsn, user=user_name, password=user_password, no_gc=1)
#
#  customTPB = ( [ fdb.isc_tpb_concurrency ] )
#  tx1=conn.trans()
#  tx2=conn.trans()
#
#  tx1.begin( tpb=customTPB )
#  tx2.begin( tpb=customTPB )
#
#  cur1=tx1.cursor()
#  cur2=tx2.cursor()
#
#  print('Tx-1: insert big number of rows.')
#  cur1.execute("insert into tbig(s) select rpad('', 50, uuid_to_char(gen_uuid())) from rdb$types,rdb$types,(select 1 k from rdb$types rows 2) rows 120000")
#  cur1.execute("insert into test(id, who) values(1, 'Tx-1')")
#  tx1.rollback()
#  print('Tx-1: rollback via TIP.')
#  cur2.execute("insert into test(id, who) values(1, 'Tx-2')")
#  print('Tx-2: insert single test record.')
#  tx2.rollback()
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    Tx-1: insert big number of rows.
    Tx-1: rollback via TIP.
    Tx-2: insert single test record.
"""

@pytest.mark.version('>=2.5.6')
def test_1(act_1: Action):
    with act_1.connect_server() as srv:
        srv.database.set_write_mode(database=str(act_1.db.db_path), mode=DbWriteMode.ASYNC)
    #
    custom_tpb = TPB(isolation=Isolation.CONCURRENCY).get_buffer()
    with act_1.db.connect(no_gc=True) as con:
        tx1 = con.transaction_manager(custom_tpb)
        tx2 = con.transaction_manager(custom_tpb)
        tx1.begin()
        tx2.begin()
        cur1 = tx1.cursor()
        cur2 = tx2.cursor()
        # Test starts here, no exception should occur
        # Tx-1: insert big number of rows.
        cur1.execute("insert into tbig(s) select rpad('', 50, uuid_to_char(gen_uuid())) from rdb$types,rdb$types,(select 1 k from rdb$types rows 2) rows 120000")
        cur1.execute("insert into test(id, who) values(1, 'Tx-1')")
        # Tx-1: rollback via TIP.
        tx1.rollback()
        # Tx-2: insert single test record.
        cur2.execute("insert into test(id, who) values(1, 'Tx-2')")
        tx2.rollback()
