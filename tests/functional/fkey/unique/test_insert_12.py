#coding:utf-8
#
# id:           functional.fkey.unique.insert_12
# title:        Check correct work fix with foreign key
# decription:   Check foreign key work.
#               Master table has one primary key field and one unique field.
#               1 Master transaction modifies non key or unique field.
#               2 Detail transaction inserts record.
#               3 Master transaction modifies unique field.
#               Detail transaction inserts record in detail_table.
#               Expected: referential integrity error
# tracker_id:
# min_versions: []
# versions:     2.5.3
# qmid:         functional.fkey.unique.ins_12

import pytest
from firebird.qa import db_factory, python_act, Action
from firebird.driver import DatabaseError, tpb, Isolation

# version: 2.5.3
# resources: None

substitutions_1 = [('lock.*', '')]

init_script_1 = """CREATE TABLE MASTER_TABLE (
    ID     INTEGER PRIMARY KEY,
    UF     INTEGER UNIQUE,
    INT_F  INTEGER
);

CREATE TABLE DETAIL_TABLE (
    ID    INTEGER PRIMARY KEY,
    FKEY  INTEGER
);

ALTER TABLE DETAIL_TABLE ADD CONSTRAINT FK_DETAIL_TABLE FOREIGN KEY (FKEY) REFERENCES MASTER_TABLE (UF);
COMMIT;
INSERT INTO MASTER_TABLE (ID, UF, INT_F) VALUES (1, 1, 10);
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
#  except Exception, e:
#    print (e[1])
#
#  try:
#    c = db_conn.cursor()
#    c.execute("update master_table set UF=10 WHERE ID=1")
#  except Exception, e:
#  print (e[0])
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    with act_1.db.connect() as con:
        cust_tpb = tpb(isolation=Isolation.READ_COMMITTED_RECORD_VERSION, lock_timeout=0)
        con.begin(cust_tpb)
        with con.cursor() as c:
            c.execute("update master_table set int_f = 10 WHERE ID=1")
            #Create second connection for change detail table
            with act_1.db.connect() as con_detail:
                con_detail.begin(cust_tpb)
                with con_detail.cursor() as cd:
                    cd.execute("INSERT INTO DETAIL_TABLE (ID, FKEY) VALUES (1,1)")
                con_detail.commit()
                with pytest.raises(DatabaseError,
                                   match='.*Foreign key references are present for the record.*'):
                    c.execute("update master_table set UF=10 WHERE ID=1")
    # Passed.
