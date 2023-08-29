#coding:utf-8

"""
ID:          issue-7723
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7723
TITLE:       Wrong error message on login if the user doesn't exists and WireCrypt is disabled
DESCRIPTION:
NOTES:
    [29.08.2023] pzotov
    1. Cursom alias must be specified in the databases.conf with:
       AuthServer = Srp256 // NOT just 'Srp'!
       Otherwise ticket issue can not be reproduced without server restart. The reason is unknown.
    2. Custom driver config objects are created here, one with WireCrypt = Disabled and second with Enabled.
    3. It is supposed that no user with name 'tmp$non_existing_7723' exists.

    Confirmed on 5.0.0.1169, 4.0.4.2979
    Checked on 5.0.0.1177, 4.0.4.2982 -- all OK.
"""

import time

import pytest
from firebird.qa import *
from firebird.driver import driver_config, connect, NetProtocol, DatabaseError

# Name of alias for self-security DB in the QA_root/files/qa-databases.conf.
# This file must be copied manually to each testing FB homw folder, with replacing
# databases.conf there:
#
REQUIRED_ALIAS = 'tmp_gh_7723_alias'

db = db_factory(filename = '#' + REQUIRED_ALIAS)
act = python_act('db')

@pytest.mark.version('>=4.0.4')
def test_1(act: Action, capsys):

    srv_cfg = driver_config.register_server(name = 'test_srv_gh_7723', config = '')
    for wc in ('Disabled', 'Enabled'):
        db_cfg_name = f'tmp_7723__wirecrypt_{wc}'
        db_cfg_object = driver_config.register_database(name = db_cfg_name)
        db_cfg_object.server.value = srv_cfg.name
        db_cfg_object.protocol.value = NetProtocol.INET
        db_cfg_object.database.value = str(act.db.db_path)
        
        db_cfg_object.config.value = f"""
            WireCrypt = {wc}
        """
        try:
            connect(db_cfg_name, user = 'tmp$non_existing_7723', password = '123')
        except DatabaseError as exc:
            print(f"WireCrypt = {wc}. Connect failed with:") # {str(exc)}")
            for x in exc.gds_codes:
                print('* gdscode:',x)
            print('* sqlcode:', exc.sqlcode)
            print('* sqlstate:', exc.sqlstate)
            print('* text:', exc.__str__())

    act.expected_stdout = """
        WireCrypt = Disabled. Connect failed with:
        * gdscode: 335544472
        * sqlcode: -902
        * sqlstate: 28000
        * text: Your user name and password are not defined. Ask your database administrator to set up a Firebird login.

        WireCrypt = Enabled. Connect failed with:
        * gdscode: 335544472
        * sqlcode: -902
        * sqlstate: 28000
        * text: Your user name and password are not defined. Ask your database administrator to set up a Firebird login.
    """

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
