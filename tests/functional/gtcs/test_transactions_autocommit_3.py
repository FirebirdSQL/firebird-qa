#coding:utf-8

"""
ID:          gtcs.transactions-autocommit-03
TITLE:       Changes within AUTO COMMIT must be cancelled when exception raises in some PROCEDURE
DESCRIPTION:
  Test does the same actions as described in GTCS/tests/AUTO_COMMIT.3.ESQL.script, see:
  https://github.com/FirebirdSQL/fbtcs/commit/166cb8b72a0aad18ef8ece34977d6d87d803616e#diff-69d4c7d7661d57fdf94aaf32a3377c82

  It creates three tables, each with single SMALLINT column (thus max value that we can put in it is 32767).
  Then it creates three procedures which do insert values in 'their' table plus call "next level" SP
  with passing there input value multiplied by 100.
  When sp_ins_1 is called with argument = 3 then sp_ins_2 will insert into test_2 table value = 300
  and sp_ins_3 will insert into test_3 value = 30000.
  This mean that we can can NOT call sp_ins_1 with values equal or more than 4 because of numeric overflow exception
  that will be raised in sp_ins_3.

  Test calls sp_ins1 two times: with arg=3 and arg=4. Second time must fail and we check that all three tables contain only
  values which are from 1st call: 3, 300 and 30000.

  NB: we use custom TPB with fdb.isc_tpb_autocommit in order to start DML transactions in AUTOCOMMIT=1 mode.
FBTEST:      functional.gtcs.transactions_autocommit_3
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stdout = """
    mon$auto_commit: 1
    x: 3
    x: 300
    x: 30000
"""

@pytest.mark.skip('FIXME: Not IMPLEMENTED')
@pytest.mark.version('>=3')
def test_1(act: Action):
    pytest.fail("Not IMPLEMENTED")

# test_script_1
#---
#
#  import os
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  import os
#  import sys
#  import inspect
#  import fdb
#
#  N_MAX=3
#
#  #CUSTOM_TX_PARAMS = ( [ fdb.isc_tpb_read_committed, fdb.isc_tpb_no_rec_version, fdb.isc_tpb_nowait, fdb.isc_tpb_autocommit ] )
#  CUSTOM_TX_PARAMS = ( [ fdb.isc_tpb_nowait, fdb.isc_tpb_autocommit ] )
#
#  db_conn.begin()
#  cx=db_conn.cursor()
#  sql_proc='''
#      create procedure sp_ins_%(i)s(a_x bigint) as
#      begin
#          insert into test_%(i)s(x) values(:a_x);
#          if ( %(i)s != %(N_MAX)s ) then
#              execute statement ( 'execute procedure sp_ins_%(k)s (?)' ) (:a_x * 100);
#      end
#  '''
#
#  for i in range(N_MAX,0,-1):
#      k = i+1
#      cx.execute( 'create table test_%(i)s(x smallint)' % locals() )
#      cx.execute( sql_proc % locals() )
#
#  db_conn.commit()
#
#  tx = db_conn.trans( default_tpb = CUSTOM_TX_PARAMS )
#
#  tx.begin()
#  cx=tx.cursor()
#
#  cx.execute('select mon$auto_commit from mon$transactions where mon$transaction_id = current_transaction')
#  for r in cx:
#      print( 'mon$auto_commit:', r[0] )
#
#  cx.callproc( 'sp_ins_1', (3,) )
#
#  try:
#      cx.callproc( 'sp_ins_1', (4,) )
#  except Exception as e:
#      pass
#      #print('Unexpected exception in ', inspect.stack()[0][3], ': ', sys.exc_info()[0])
#      #print(e)
#
#  tx.commit()
#
#  cx = db_conn.cursor()
#  cx.execute('select x from test_1 union all select x from test_2 union all select x from test_3')
#  for r in cx:
#      print( 'x:', r[0])
#
#  cx.close()
#  tx.close()
#  db_conn.close()
#
#---
