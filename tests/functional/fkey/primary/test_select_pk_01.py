#coding:utf-8
#
# id:           functional.fkey.primary.select_pk_01
# title:        Check correct work fix with foreign key
# decription:   Check foreign key work.
#               Master transaction is perform select with lock and fetch record.
#               Detail transaction inserts record in detail_table.
#               Expected: no errors.
# tracker_id:
# min_versions: []
# versions:     2.5
# qmid:         functional.fkey.primary.select_01

import pytest
from firebird.qa import db_factory, python_act, Action
from firebird.driver import tpb, Isolation

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
#  c.execute("SELECT INT_F FROM MASTER_TABLE WHERE ID=1 WITH LOCK")
#  c.fetchall()
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
#  print (e[0])
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    with act_1.db.connect() as con:
        cust_tpb = tpb(isolation=Isolation.READ_COMMITTED_RECORD_VERSION, lock_timeout=0)
        con.begin(cust_tpb)
        with con.cursor() as c:
            c.execute("SELECT INT_F FROM MASTER_TABLE WHERE ID=1 WITH LOCK").fetchall()
            con.commit()
            #Create second connection for change detail table
            with act_1.db.connect() as con_detail:
                con_detail.begin(cust_tpb)
                with con_detail.cursor() as cd:
                    cd.execute("INSERT INTO DETAIL_TABLE (ID, FKEY) VALUES (1,1)")
                con_detail.commit()
    # Passed.
