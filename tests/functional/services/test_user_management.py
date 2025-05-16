#coding:utf-8

"""
ID:          services.user-management
TITLE:       Check ability to make connect to FB services and add/drop user
DESCRIPTION:
  We check here:
  1) FB services features which add and remove user;
  2) Python firebird-driver functions (from class Server)

  NB.
  User with name 'tmp_vaclav' must NOT present in security_db.
  Results are verified by attempts to make TCP connection to the test DB using login/password of this user.

  See doc:
    https://firebird-driver.readthedocs.io/en/latest/usage-guide.html#user-maintenance
    https://firebird-driver.readthedocs.io/en/latest/ref-core.html#firebird.driver.core.Server.user
    https://firebird-driver.readthedocs.io/en/latest/ref-core.html#serveruserservices
FBTEST:      functional.services.user_management
"""
import sys
import pytest
from firebird.qa import *
import firebird.driver
from firebird.driver import TPB, Isolation, core as fb_core, DatabaseError

#sys.stdout.reconfigure(encoding='utf-8')

db = db_factory(init = "create sequence g;")

act = python_act('db')

@pytest.mark.version('>=3')
def test_1(act: Action, capsys):
    
    #----------------------------------------------------------
    def print_user_data(con, cur, prepared_sttm, mode, uname):
        con.commit()
        con.begin()
        cur.execute(prepared_sttm, (uname,))
        col_hdr=cur.description
        for r in cur:
            for i in range(0,len(col_hdr)):
                print( (col_hdr[i][0] +':').ljust(32), r[i] )
        if mode != 'del':
            if cur.affected_rows == 0:
                cur.execute('select sec$user_name from sec$users')
                existing_users = '\n'.join( [r[0].rstrip() for r in cur.fetchall()] )
                assert False, f"Problem with security.db for {mode=}: could not find expected record with sec$user_name = '{uname}' using charset = {con.charset}, {existing_users=}"
        else:
            assert cur.affected_rows == 0, f"Problem with security.db for {mode=}: UNEXPECTED record encountered with sec$user_name = '{uname}', {cur.affected_rows=}"

    #----------------------------------------------------------

    TMP_USER_NAME = 'tmp_vaclav'.upper()
    
    # ::: NOTE :::
    # >  spb.insert_string(SrvUserOption.USER_NAME, user_name, encoding=self._srv().encoding)
    # self.vtable.insertString(self, self.status, tag, value.encode(encoding, errors))
    # UnicodeEncodeError: 'ascii' codec can't encode character '\xe1' in position 5: ordinal not in range(128)
    #TMP_USER_NAME = '"tmp_Václav"'

    sttm = 'select gen_id(g,1) as point, sec$user_name, sec$first_name, sec$last_name, sec$admin from rdb$database join sec$users on sec$user_name = ?'

    with act.db.connect(charset = 'utf8') as con:
        con.begin()
        cur = con.cursor()
        
        prepared_sttm = cur.prepare(sttm)

        with act.connect_server() as srv:
            svc = fb_core.ServerUserServices(srv)
    
            # not helped for non-ascii user name: 
            svc._srv().encoding = con.charset
            # print(svc._srv().encoding)

            if svc.exists(user_name = TMP_USER_NAME):
                svc.delete(user_name = TMP_USER_NAME)

            svc.add( user_name = TMP_USER_NAME, password = '123', first_name = 'John', last_name = 'Smith', admin = True)
            print_user_data(con, cur, prepared_sttm, 'add', TMP_USER_NAME)

            # Here we make sure that user actually exists and can make connecttion:
            with act.db.connect(user = TMP_USER_NAME, password = '123', charset = con.charset) as con_check:
                pass

            svc.update( user_name = TMP_USER_NAME, last_name = 'Jackson', admin = False, first_name = 'Robert')
            print_user_data(con, cur, prepared_sttm, 'upd', TMP_USER_NAME)

            svc.delete(user_name = TMP_USER_NAME)
            print_user_data(con, cur, prepared_sttm, 'del', TMP_USER_NAME)
            try:
                with act.db.connect(user = TMP_USER_NAME, password = '123') as con_check:
                    print('UNEXPECTED: user must not exist at this point!')
            except DatabaseError as e:
                # 335544472 ==> Your user name and password are not defined ...
                for x in e.gds_codes:
                    print(x)

    expected_out = f"""
        POINT:                           1
        SEC$USER_NAME:                   {TMP_USER_NAME}
        SEC$FIRST_NAME:                  John
        SEC$LAST_NAME:                   Smith
        SEC$ADMIN:                       True

        POINT:                           2
        SEC$USER_NAME:                   {TMP_USER_NAME}
        SEC$FIRST_NAME:                  Robert
        SEC$LAST_NAME:                   Jackson
        SEC$ADMIN:                       False

        335544472
    """

    act.expected_stdout = expected_out
    act.stdout = capsys.readouterr().out

    assert act.clean_stdout == act.clean_expected_stdout
