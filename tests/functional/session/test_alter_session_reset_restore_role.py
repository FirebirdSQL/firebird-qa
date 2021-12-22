#coding:utf-8
#
# id:           functional.session.alter_session_reset_restore_role
# title:        
#                   ALTER SESSION RESET: restore ROLE which was passed with DPB and clear all cached security classes (if role was changed)
#                
# decription:   
#                  Test issue from CORE-5832 about ALTER SESSION RESET:
#                  "restore ROLE which was passed with DPB and clear all cached security classes (if role was changed) ".
#               
#                  NOTE. *** SET AUTODDL OFF REQUIRED ***
#                      Following is detailed explanation of this note:
#                      ========
#                          Default ISQL behaviour is to start always *TWO* transactions (for DML and second for DDL)
#                          after previous commit / rollback and before *ANY* further satement is to be executed, except
#                          those which control ISQL itself (e.g. 'SET TERM'; 'IN ...'; 'SET BAIL' etc).
#                          So, even when statement <S> has nothing to change, ISQL will start TWO transactions
#                          just before executing <S>.
#                          This means that these transactions will start even if want to run 'ALTER SESSION RESET'.
#                          This, in turn, makes one of them (which must perform DDL) be 'active and NOT current'
#                          from ALTER SESSION point of view (which is run within DML transaction).
#               
#                          According to description given in CORE-5832, ALTER SESSION throws error isc_ses_reset_err
#                          "if any open transaction exist in current conneciton, *except of current transaction* and
#                          prepared 2PC transactions which is allowed and ignored by this check".
#               
#                          So, we have to prohibit 'autostart' of DDL-transaction because otherwise ALTER SESSION will
#                          throw: "SQLSTATE = 01002 / Cannot reset user session / -There are open transactions (2 active)".
#                          This is done by 'SET AUTODDL OFF' statement at the beginning of this test script.
#                      ========
#               
#                  Thanks to Vlad for explanations (discussed 18.01.2021).
#                  Checked on 4.0.0.2307 SS/CS.
#                
# tracker_id:   
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bail on;

    create role acnt;
    create role boss;
    commit;

    create view v_test as
    select mon$user as who_ami, mon$role as whats_my_role
    from mon$attachments
    where mon$attachment_id = current_connection;
    commit;

    grant acnt to sysdba;
    grant boss to sysdba;
    commit;

    set list on;
    set autoddl off;
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey' role boss;

    select * from v_test;
    set role acnt;
    commit;
    select * from v_test;

    --------------------
    alter session reset;
    --------------------
    select * from v_test;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WHO_AMI                         SYSDBA
    WHATS_MY_ROLE                   BOSS

    WHO_AMI                         SYSDBA
    WHATS_MY_ROLE                   ACNT

    WHO_AMI                         SYSDBA
    WHATS_MY_ROLE                   BOSS
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

