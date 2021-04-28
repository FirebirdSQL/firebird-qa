#coding:utf-8
#
# id:           functional.fkey.primary.insert_pk_01
# title:        Check correct work fix with foreign key
# decription:   Check foreign key work.
#               Master transaction doesn't modify primary key.
#               Detail transaction inserts record in detail_table.
#               Expected: no errors
# tracker_id:   
# min_versions: []
# versions:     2.5
# qmid:         functional.fkey.primary.ins_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE MASTER_TABLE (
    ID     INTEGER PRIMARY KEY,
    INT_F  INTEGER
);

CREATE TABLE DETAIL_TABLE (
    ID    INTEGER PRIMARY KEY,
    FKEY  INTEGER
);

ALTER TABLE DETAIL_TABLE ADD CONSTRAINT FK_DETAIL_TABLE FOREIGN KEY (FKEY) REFERENCES MASTER_TABLE (ID);
COMMIT;
INSERT INTO MASTER_TABLE (ID, INT_F) VALUES (1, 10);
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# TPB_master = (
#        chr(kdb.isc_tpb_write)
#      + chr(kdb.isc_tpb_read_committed) + chr(kdb.isc_tpb_rec_version)
#      + chr(kdb.isc_tpb_nowait)
#                    )
#  TPB_detail = (
#        chr(kdb.isc_tpb_write)
#      + chr(kdb.isc_tpb_read_committed) + chr(kdb.isc_tpb_rec_version)
#      + chr(kdb.isc_tpb_nowait)
#                    )
#  
#  db_conn.begin(tpb=TPB_master)
#  c = db_conn.cursor()
#  c.execute("update master_table set int_f = 10 WHERE ID=1")
#  
#  #Create second connection for change detail table
#  con_detail = kdb.connect(
#       dsn=dsn.encode(),
#       user=user_name.encode(),
#       password=user_password.encode()
#  )
#  
#  try:
#    con_detail.begin(tpb=TPB_detail)
#    c = con_detail.cursor()
#    c.execute("INSERT INTO DETAIL_TABLE (ID, FKEY) VALUES (1,1)")
#    con_detail.commit()
#  except Exception, e:
#    print (e[0])
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


