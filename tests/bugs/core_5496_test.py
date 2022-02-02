#coding:utf-8

"""
ID:          issue-5765
ISSUE:       5765
TITLE:       Creating SRP SYSDBA with explicit admin (-admin yes in gsec or grant admin
  role in create user) creates two SYSDBA accounts
DESCRIPTION:
  Test script should display only ONE record.
NOTES:
[8.12.2021] [pcisar]
  On Linux it fails with:
  Statement failed, SQLSTATE = 28000
  no permission for remote access to database security.db
JIRA:        CORE-5496
FBTEST:      bugs.core_5496
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stdout = """
    SEC$USER_NAME                   SYSDBA
    SEC$PLUGIN                      Srp
    Records affected: 1
"""

test_script = """
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

@pytest.mark.skip('FIXME: remote access to security.db')
@pytest.mark.version('>=3.0.2')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q', '-b'], input=test_script)
    assert act.clean_stdout == act.clean_expected_stdout
