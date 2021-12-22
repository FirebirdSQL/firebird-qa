#coding:utf-8
#
# id:           bugs.core_1642
# title:        Non-privileged monitoring reports wrong attachment data
# decription:
#                   When non-SYSDBA user selects from MON$ATTACHMENTS and other attachments are active at this point,
#                   the resulting rowset refers to a wrong attachment (the one with minimal ID) instead of the current attachment.
#                   Checked on: 4.0.0.1635; 3.0.5.33180; 2.5.9.27119.
#
# tracker_id:   CORE-1642
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action, user_factory, User

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """
    create or alter view v_my_attach as
    select current_user as who_am_i, iif(current_connection - mon$attachment_id = 0, 'OK.', 'BAD') as my_attach_id
    from mon$attachments;
    commit;

    grant select on v_my_attach to public;
    commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  con1=fdb.connect( dsn = dsn, user = 'tmp$c1642_alan', password = '123')
#  con2=fdb.connect( dsn = dsn, user = 'tmp$c1642_john', password = '456')
#  con3=fdb.connect( dsn = dsn, user = 'tmp$c1642_mick', password = '789')
#
#  cur1=con1.cursor()
#  cur2=con2.cursor()
#  cur3=con3.cursor()
#
#  chk_sql='select who_am_i, my_attach_id from v_my_attach'
#  cur1.execute(chk_sql)
#  cur2.execute(chk_sql)
#  cur3.execute(chk_sql)
#
#  for c in (cur1,cur2,cur3):
#      for r in c:
#          print(r[0],r[1])
#
#  cur1.close()
#  cur2.close()
#  cur3.close()
#  con1.close()
#  con2.close()
#  con3.close()
#
#  db_conn.execute_immediate('drop user tmp$c1642_alan')
#  db_conn.execute_immediate('drop user tmp$c1642_john')
#  db_conn.execute_immediate('drop user tmp$c1642_mick')
#  db_conn.commit()
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    TMP$C1642_ALAN OK.
    TMP$C1642_JOHN OK.
    TMP$C1642_MICK OK.
"""

user_1 = user_factory('db_1', name='tmp$c1642_alan', password='123')
user_2 = user_factory('db_1', name='tmp$c1642_john', password = '456')
user_3 = user_factory('db_1', name='tmp$c1642_mick', password = '789')

@pytest.mark.version('>=2.5')
def test_1(act_1: Action, user_1: User, user_2: User, user_3: User, capsys):
    act_1.expected_stdout = expected_stdout_1
    for user in [user_1, user_2, user_3]:
        with act_1.db.connect(user=user.name, password=user.password) as con:
            c = con.cursor()
            c.execute('select who_am_i, my_attach_id from v_my_attach')
            for row in c:
                print(row[0], row[1])
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout





