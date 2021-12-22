#coding:utf-8
#
# id:           bugs.core_3511
# title:        Unquoted role names with non-ASCII characters passed in DPB are upper-cased wrongly
# decription:
#                   Test creates role with non-ascii characters and grants it to common user.
#                   Then we try to connect to database using this role and specify it WITHOUT double quotes.
#
#                   ::: NB ::: DIFFERENT CODE FOR LINUX vs WINDOWS :::
#
#                   Attribute 'test_type' can be 'ISQL' only under LINUX.
#
#                   As of Windows, only system code page can be used when ISQL passes user/role containing non-ascii characters
#                   (see letter from dimitr, 12-mar-2016, 19:14).
#
#                   Because of this, it was decided to use Pytthon FDB for connect with DPB that contains non-ascii data.
#                   FDB method connect() of class Connection has parameter 'utf8params' with possible values True | False.
#                   When this parameter is True, all info passed to DPB in UTF-8. Test uses this to form proper DPB and connect
#                   to database with non-ascii role. This role must be specified WITHOUT double quotes.
#
#                   Checked on Linux:  3.0.8.33445, 4.0.0.2437
#                   Checked on Windows 3.0.8.33452, 4.0.0.2436
#
# tracker_id:
# min_versions: ['3.0']
# versions:     3.0, 3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, python_act, Action, user_factory, User

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set wng off;
    set bail on;
    create or alter view v_whoami as
    select current_user as cur_user,mon$role as mon_role,current_role as cur_role
    from mon$attachments
    where mon$attachment_id=current_connection;

    revoke all on all from tmp$c3511;
    commit;

    create table test(id int);

    create role "Gros";
    create role "Groß";
    create role "αβγδε";

    grant "Gros" to tmp$c3511;
    grant "Groß" to tmp$c3511;
    grant "αβγδε" to tmp$c3511;
    commit;

    grant select on v_whoami to tmp$c3511;
    grant select on test to role "Gros";
    grant select on test to role "Groß";
    grant select on test to role "αβγδε";
    commit;

    set list on;

    set bail off;
    -- NB: do NOT enclose role name into double quotes here:
    connect '$(DSN)' user tmp$c3511 password '123' role αβγδε;
    select * from v_whoami;
    set plan on;
    select * from test;
    set plan off;
    commit;

    -- NB: do NOT enclose role name into double quotes here:
    connect '$(DSN)' user tmp$c3511 password '123' role Groß;
    select * from v_whoami;
    set plan on;
    select * from test;
    set plan off;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CUR_USER                        TMP$C3511
    MON_ROLE                        αβγδε
    CUR_ROLE                        αβγδε
    PLAN (TEST NATURAL)

    CUR_USER                        TMP$C3511
    MON_ROLE                        Groß
    CUR_ROLE                        Groß
    PLAN (TEST NATURAL)
"""

user_1 = user_factory('db_1', name='tmp$c3511', password='123', plugin='Srp')

@pytest.mark.version('>=3.0')
@pytest.mark.platform('Linux')
def test_1(act_1: Action, user_1: User):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 3.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

# test_script_2
#---
#
#  import os
#
#  os.environ["ISC_USER"] = 'SYSDBA'
#  os.environ["ISC_PASSWORD"] = 'masterkey'
#
#  cur = db_conn.cursor()
#  cur.execute("create or alter user tmp$c3511 password '123' using plugin Srp")
#  cur.execute('create table test(id int)')
#  cur.execute('create role "Groß"')
#  db_conn.commit()
#
#  cur.execute('grant "Groß" to tmp$c3511')
#  cur.execute('grant select on test to "Groß"')
#  db_conn.commit()
#
#  # NB: do NOT enclose rolename Groß in double quotes here
#  # (this was needed in FB 2.5.x only; should NOT be necessarry in FB 3.x+):
#  con=fdb.connect(dsn = dsn, charset = 'utf8', utf8params = True, user = 'tmp$c3511', password = '123', role='Groß')
#
#  cur=con.cursor()
#  cur.execute("select * from test");
#  for r in cur:
#      pass
#
#  print('Done.')
#  cur.close()
#  con.close()
#
#  con=fdb.connect(dsn = dsn)
#  con.execute_immediate('drop user tmp$c3511 using plugin Srp')
#  con.commit()
#  con.close()
#
#
#---

act_2 = python_act('db_2', substitutions=substitutions_2)

expected_stdout_2 = """
    Done.
"""

test_user_2 = user_factory('db_2', name='tmp$c3511', password='123', plugin='Srp')

@pytest.mark.version('>=3.0')
@pytest.mark.platform('Windows')
def test_2(act_2: Action, test_user_2: User):
    pytest.fail("Test not IMPLEMENTED")


