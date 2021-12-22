#coding:utf-8
#
# id:           bugs.core_2573
# title:        The server crashes when selecting from the MON$ tables in the ON DISCONNECT trigger
# decription:
# tracker_id:   CORE-2573
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# sql = """CREATE OR ALTER TRIGGER DIST
#  ON DISCONNECT POSITION 0
#  AS
#  declare variable i integer;
#  begin
#    select mon$stat_id from mon$attachments rows 1 into :i;
#  end
#  """
#
#  c = db_conn.cursor()
#  c.execute(sql)
#  db_conn.commit()
#  db_conn.close()
#
#  db_conn = kdb.connect(dsn=dsn,user=user_name,password=user_password)
#  c = db_conn.cursor()
#  c.execute("DROP TRIGGER DIST")
#  db_conn.commit()
#  db_conn.close()
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    sql = """CREATE OR ALTER TRIGGER DIST
    ON DISCONNECT POSITION 0
    AS
    declare variable i integer;
    begin
      select mon$stat_id from mon$attachments rows 1 into :i;
    end
"""
    with act_1.db.connect() as con:
        c = con.cursor()
        c.execute(sql)
        con.commit()
    # The server should could be crashed at this point
    with act_1.db.connect() as con:
        c = con.cursor()
        c.execute('DROP TRIGGER DIST')
        con.commit()


