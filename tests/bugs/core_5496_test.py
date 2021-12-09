#coding:utf-8
#
# id:           bugs.core_5496
# title:        Creating SRP SYSDBA with explicit admin (-admin yes in gsec or grant admin role in create user) creates two SYSDBA accounts
# decription:
#                   Test script should display only ONE record.
#                   Confirmed problem on:
#                       3.0.0.32483: three(!) records are displayed instead of one.
#                       3.0.1.32609: no records displayed with 'sysdba' account.
#                   Confirmed bug on 3.0.2.32658, WI-V3.0.2.32691.
#
#                   Checked on 3.0.2.32703: all OK.
#                   Checked on 4.0.0.1479, 3.0.5.33115 - all fine.
#
#                   03-mar-2021: replaced 'xnet' with 'localhost' in order have ability to run this test on Linux.
#
#               [pcisar] 8.12.2021
#               Fails with "no permission for remote access to database security.db" on Linux FB 4.0
#
# tracker_id:   CORE-5496
# min_versions: ['3.0.2']
# versions:     3.0.2
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.close()
#
#  check_sql='''
#      -- connect 'xnet://security.db';
#      connect 'localhost:security.db';
#      create or alter user foo password '123' grant admin role using plugin Srp;
#      create or alter user rio password '123' grant admin role using plugin Srp;
#      create or alter user bar password '123' grant admin role using plugin Srp;
#      commit;
#      grant rdb$admin to sysdba granted by foo;
#      grant rdb$admin to sysdba granted by rio;
#      grant rdb$admin to sysdba granted by bar;
#      commit;
#      set list on;
#      set count on;
#      select sec$user_name, sec$plugin from sec$users where upper(sec$user_name) = upper('sysdba') and upper(sec$plugin) = upper('srp');
#      commit;
#
#      drop user foo using plugin Srp;
#      drop user rio using plugin Srp;
#      drop user bar using plugin Srp;
#      commit;
#      quit;
#  '''
#
#  runProgram('isql', ['-q'], check_sql)
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    SEC$USER_NAME                   SYSDBA
    SEC$PLUGIN                      Srp
    Records affected: 1
"""

test_script_1 = """
    connect 'localhost:security.db';
    create or alter user foo password '123' grant admin role using plugin Srp;
    create or alter user rio password '123' grant admin role using plugin Srp;
    create or alter user bar password '123' grant admin role using plugin Srp;
    commit;
    grant rdb$admin to sysdba granted by foo;
    grant rdb$admin to sysdba granted by rio;
    grant rdb$admin to sysdba granted by bar;
    commit;
    set list on;
    set count on;
    select sec$user_name, sec$plugin from sec$users where upper(sec$user_name) = upper('sysdba') and upper(sec$plugin) = upper('srp');
    commit;

    drop user foo using plugin Srp;
    drop user rio using plugin Srp;
    drop user bar using plugin Srp;
    commit;
    quit;
"""

@pytest.mark.version('>=3.0.2')
def test_1(act_1: Action):
    pytest.skip("Requires remote access to security.db")
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=['-q', '-b'], input=test_script_1)
    assert act_1.clean_stdout == act_1.clean_expected_stdout


