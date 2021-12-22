#coding:utf-8
#
# id:           bugs.core_2233
# title:        Allow non-SYSDBA users to monitor not only their current attachment but other their attachments as well
# decription:
#                   Checked on:
#                       4.0.0.1635 SS: OK, 1.605s.   4.0.0.1633 CS: OK, 2.133s.
#                       3.0.5.33180 SS: OK, 1.925s.  3.0.5.33178 CS: OK, 1.581s.
#                       2.5.9.27119 SC: OK, 0.338s.  2.5.9.27146 SS: OK, 0.317s.
#
# tracker_id:   CORE-2233
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action, user_factory, User, role_factory, Role

# version: 2.5
# resources: None

substitutions_1 = [('[ \t]+', ' '), ('=', '')]

#init_script_1 = """
    #set wng off;
    #-- Drop old account if it remains from prevoius run:
    #set term ^;
    #execute block as
    #begin
        #begin
            #execute statement 'drop user tmp$c2233_adam' with autonomous transaction;
            #when any do begin end
        #end
        #begin
            #execute statement 'drop user tmp$c2233_mike' with autonomous transaction;
            #when any do begin end
        #end
        #begin
            #execute statement 'drop role tmp$r2233_boss';
            #when any do begin end
        #end
    #end
    #^
    #set term ;^
    #commit;

    #create user tmp$c2233_adam password '123';
    #create user tmp$c2233_mike password '456';
    #commit;
    #create role tmp$r2233_boss;
    #create role tmp$r2233_acnt;
    #grant tmp$r2233_boss to tmp$c2233_adam;
    #grant tmp$r2233_acnt to tmp$c2233_adam;
    #commit;
#"""

db_1 = db_factory(sql_dialect=3, init='')

# test_script_1
#---
#
#  con0=fdb.connect( dsn = dsn, user='tmp$c2233_mike', password='456' )
#  con1=fdb.connect( dsn = dsn, user='tmp$c2233_adam', password='123' )
#  con2=fdb.connect( dsn = dsn, user='tmp$c2233_adam', password='123' )
#  con3=fdb.connect( dsn = dsn, user='tmp$c2233_adam', password='123', role='tmp$r2233_boss' )
#  con4=fdb.connect( dsn = dsn, user='tmp$c2233_adam', password='123', role='tmp$r2233_acnt' )
#
#  chk_sql='''
#      select current_user as who_am_i, mon$user mon_att_user, mon$role as mon_att_role, count( mon$user ) as mon_att_cnt
#      from rdb$database r
#      left join mon$attachments a on a.mon$attachment_id != current_connection
#      group by 1,2,3
#  '''
#
#  cur_mngr=con0.cursor()
#  cur_mngr.execute(chk_sql)
#  cur_cols=cur_mngr.description
#  for r in cur_mngr:
#      for i in range(0,len(cur_cols)):
#          print( cur_cols[i][0],':', r[i] )
#  cur_mngr.close()
#  #-------------------------------------------
#
#  cur_boss=con1.cursor()
#  cur_boss.execute(chk_sql)
#  cur_cols=cur_boss.description
#  for r in cur_boss:
#      for i in range(0,len(cur_cols)):
#          print( cur_cols[i][0],':', r[i] )
#  cur_boss.close()
#  #-------------------------------------------
#
#  for c in (con0,con1,con2,con3,con4):
#      c.close()
#
#  db_conn.execute_immediate('drop user tmp$c2233_adam')
#  db_conn.execute_immediate('drop user tmp$c2233_mike')
#  db_conn.commit()
#
#  ##                                    ||||||||||||||||||||||||||||
#  ## ###################################|||  FB 4.0+, SS and SC  |||##############################
#  ##                                    ||||||||||||||||||||||||||||
#  ## If we check SS or SC and ExtConnPoolLifeTime > 0 (config parameter FB 4.0+) then current
#  ## DB (bugs.core_NNNN.fdb) will be 'captured' by firebird.exe process and fbt_run utility
#  ## will not able to drop this database at the final point of test.
#  ## Moreover, DB file will be hold until all activity in firebird.exe completed and AFTER this
#  ## we have to wait for <ExtConnPoolLifeTime> seconds after it (discussion and small test see
#  ## in the letter to hvlad and dimitr 13.10.2019 11:10).
#  ## This means that one need to kill all connections to prevent from exception on cleanup phase:
#  ## SQLCODE: -901 / lock time-out on wait transaction / object <this_test_DB> is in use
#  ## #############################################################################################
#  db_conn.execute_immediate('delete from mon$attachments where mon$attachment_id != current_connection')
#  db_conn.commit()
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

user_mike = user_factory('db_1', name='tmp$c2233_mike', password='456')
user_adam = user_factory('db_1', name='tmp$c2233_adam', password='123')

expected_stdout_1 = """
    WHO_AM_I 		: TMP$C2233_MIKE
    MON_ATT_USER 	: None
    MON_ATT_ROLE 	: None
    MON_ATT_CNT 	: 0

    WHO_AM_I 		: TMP$C2233_ADAM
    MON_ATT_USER 	: TMP$C2233_ADAM
    MON_ATT_ROLE 	: NONE
    MON_ATT_CNT 	: 1

    WHO_AM_I 		: TMP$C2233_ADAM
    MON_ATT_USER 	: TMP$C2233_ADAM
    MON_ATT_ROLE 	: TMP$R2233_ACNT
    MON_ATT_CNT 	: 1

    WHO_AM_I 		: TMP$C2233_ADAM
    MON_ATT_USER 	: TMP$C2233_ADAM
    MON_ATT_ROLE 	: TMP$R2233_BOSS
    MON_ATT_CNT 	: 1
"""

boss = role_factory('db_1', name='tmp$r2233_boss')
acnt = role_factory('db_1', name='tmp$r2233_acnt')

@pytest.mark.version('>=2.5')
def test_1(act_1: Action, user_mike: User, user_adam: User, boss: Role, acnt: Role, capsys):
    act_1.expected_stdout = expected_stdout_1
    with act_1.db.connect() as con:
        c = con.cursor()
        c.execute('grant tmp$r2233_boss to tmp$c2233_adam')
        c.execute('grant tmp$r2233_acnt to tmp$c2233_adam')
        con.commit()
        #
        with act_1.db.connect(user=user_mike.name, password=user_mike.password) as con0, \
             act_1.db.connect(user=user_adam.name, password=user_adam.password) as con1, \
             act_1.db.connect(user=user_adam.name, password=user_adam.password) as con2, \
             act_1.db.connect(user=user_adam.name, password=user_adam.password, role=boss.name) as con3, \
             act_1.db.connect(user=user_adam.name, password=user_adam.password, role=acnt.name) as con4:
            #
            chk_sql = '''
                select current_user as who_am_i, mon$user mon_att_user, mon$role as mon_att_role, count( mon$user ) as mon_att_cnt
                from rdb$database r
                left join mon$attachments a on a.mon$attachment_id != current_connection
                group by 1,2,3
            '''
            #
            cur_mngr = con0.cursor()
            cur_mngr.execute(chk_sql)
            cur_cols = cur_mngr.description
            for r in cur_mngr:
                for i in range(0,len(cur_cols)):
                    print( cur_cols[i][0], ':', r[i] )
            cur_mngr.close()
            #
            cur_boss = con1.cursor()
            cur_boss.execute(chk_sql)
            cur_cols = cur_boss.description
            for r in cur_boss:
                for i in range(0,len(cur_cols)):
                    print( cur_cols[i][0], ':', r[i] )
            cur_boss.close()
            #
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
