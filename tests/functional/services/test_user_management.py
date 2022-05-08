#coding:utf-8

"""
ID:          services.user-management
TITLE:       Check ability to make connect to FB services and add/drop user
DESCRIPTION:
  We check here:
  1) FB services features which add and remove user;
  2) Python firebird-driver functions (from class Server)

  NB.
  User with name 'tmp$test$user$' must NOT present in security_db.
  Correctness of adding user is verified by establishing TCP-based attachment to test DB using its login/password.

  See doc:
    https://firebird-driver.readthedocs.io/en/latest/usage-guide.html#user-maintenance
    https://firebird-driver.readthedocs.io/en/latest/ref-core.html#firebird.driver.core.Server.user
    https://firebird-driver.readthedocs.io/en/latest/ref-core.html#serveruserservices
FBTEST:      functional.services.user_management
"""

import pytest
from firebird.qa import *
import firebird.driver
from firebird.driver import TPB, Isolation, core as fb_core

db = db_factory(init = "create sequence g;")

act = python_act('db')

test_expected_stdout = """
    POINT:                           1
    SEC$USER_NAME:                   TMP$TEST$USER
    SEC$FIRST_NAME:                  John
    SEC$LAST_NAME:                   Smith
    SEC$ADMIN:                       True

    POINT:                           2
    SEC$USER_NAME:                   TMP$TEST$USER
    SEC$FIRST_NAME:                  Robert
    SEC$LAST_NAME:                   Jackson
    SEC$ADMIN:                       False

    POINT:                           3
    SEC$USER_NAME:                   None
    SEC$FIRST_NAME:                  None
    SEC$LAST_NAME:                   None
    SEC$ADMIN:                       None
"""

@pytest.mark.version('>=3')
def test_1(act: Action, capsys):
    
    #----------------------------------------------------------
    def print_user_data(con, cur, prepared_sttm):
        con.commit()
        con.begin()
        cur.execute(prepared_sttm, (TMP_USER_NAME,))
        col_hdr=cur.description
        for r in cur:
            for i in range(0,len(col_hdr)):
                print( (col_hdr[i][0] +':').ljust(32), r[i] )
    #----------------------------------------------------------

    TMP_USER_NAME = 'tmp$test$user'.upper()
    sttm = 'select gen_id(g,1) as point, sec$user_name, sec$first_name, sec$last_name, sec$admin from rdb$database left join sec$users on sec$user_name = ?'

    with act.db.connect() as con:
        con.begin()
        cur = con.cursor()
        prepared_sttm = cur.prepare(sttm)

        with act.connect_server() as srv:
            svc = fb_core.ServerUserServices(srv)
            if svc.exists(user_name = TMP_USER_NAME):
                svc.delete(user_name = TMP_USER_NAME)

            svc.add( user_name = TMP_USER_NAME, password = '123', first_name = 'John', last_name = 'Smith', admin = True)
            print_user_data(con, cur, prepared_sttm)

            # Here we make sure that user actually exists and can make connecttion:
            with act.db.connect(user = TMP_USER_NAME, password = '123') as con_check:
                pass

            svc.update( user_name = TMP_USER_NAME, last_name = 'Jackson', admin = False, first_name = 'Robert')
            print_user_data(con, cur, prepared_sttm)

            svc.delete(user_name = TMP_USER_NAME)
            print_user_data(con, cur, prepared_sttm)

    act.expected_stdout = test_expected_stdout
    act.stdout = capsys.readouterr().out

    assert act.clean_stdout == act.clean_expected_stdout
