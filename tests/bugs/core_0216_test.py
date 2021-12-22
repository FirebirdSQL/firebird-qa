#coding:utf-8
#
# id:           bugs.core_0216
# title:        Too many grants lose privileges
# decription:   Issuing more than 2000 grants on any one object causes
#               an internal buffer flow in generating the access
#               control list that actually enforces the rights.
# tracker_id:   CORE-216
# min_versions: ['2.5']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """create table T (PK integer);
create table LOG(PK integer);
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  # Create 4000 triggers on table T
#  i = 1
#  cmd = """create trigger LOGT_%d for T after insert as
#  begin
#    insert into log (PK) values (new.pk);
#  end
#  """
#  while i <= 4000:
#      c.execute(cmd % i)
#      i += 1
#  db_conn.commit()
#
#  # Grants
#  i = 1
#  cmd = """GRANT INSERT ON LOG TO TRIGGER LOGT_%d"""
#  while i <= 4000:
#      try:
#          c.execute(cmd % i)
#      except Exception as e:
#          print('Error:',e)
#          i = 4000
#      i += 1
#  db_conn.commit()
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    with act_1.db.connect() as con:
        c = con.cursor()
        # Create 4000 triggers on table T
        i = 1
        cmd = """create trigger LOGT_%d for T after insert as
        begin
          insert into log (PK) values (new.pk);
        end
"""
        while i <= 4000:
            c.execute(cmd % i)
            i += 1
        con.commit()
        # Grants
        i = 1
        cmd = """GRANT INSERT ON LOG TO TRIGGER LOGT_%d"""
        while i <= 4000:
            c.execute(cmd % i)
            i += 1
        con.commit()


