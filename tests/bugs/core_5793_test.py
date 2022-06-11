#coding:utf-8

"""
ID:          issue-6056
ISSUE:       6056
TITLE:       Error returned from DbCryptPlugin::setKey() is not shown
DESCRIPTION:
    Test issues: 'alter database encrypt ...' with NON existing key and check exception that will raise.

JIRA:        CORE-5793
FBTEST:      bugs.core_5793
NOTES:
    [12.06.2022] pzotov
    Checked on 4.0.1.2692, 3.0.8.33535 - both on Linux and Windows.
"""

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError

db = db_factory()

act = python_act('db')

ENCRYPTION_PLUGIN = 'fbSampleDbCrypt'
ENCRYPTION_HOLDER = 'fbSampleKeyHolder'
ENCRYPTION_BADKEY = 'NoSuchKey'

fb3x_checked_stdout = f"""
    unsuccessful metadata update
    -ALTER DATABASE failed
    -Missing correct crypt key
    -Plugin {ENCRYPTION_HOLDER}:
    -Crypt key {ENCRYPTION_BADKEY} not set
"""

fb4x_checked_stdout = f"""
    unsuccessful metadata update
    -ALTER DATABASE failed
    -Missing database encryption key for your attachment
    -Plugin {ENCRYPTION_HOLDER}:
    -Crypt key {ENCRYPTION_BADKEY} not set
"""

@pytest.mark.encryption
@pytest.mark.version('>=3.0.4')
def test_1(act: Action, capsys):
    
        with act.db.connect() as con:
            sttm = f'alter database encrypt with "{ENCRYPTION_PLUGIN}" key "{ENCRYPTION_BADKEY}"'
            try:
                con.execute_immediate(sttm)
            except DatabaseError as e:
                print( e.__str__() )

            act.expected_stdout = fb3x_checked_stdout if act.is_version('<4') else fb4x_checked_stdout
            act.stdout = capsys.readouterr().out
            assert act.clean_stdout == act.clean_expected_stdout
