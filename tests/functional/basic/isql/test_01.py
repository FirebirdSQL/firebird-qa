#coding:utf-8

"""
ID:          isql-02
TITLE:       ISQL - SHOW DATABASE
DESCRIPTION: Check for correct output of SHOW DATABASE on empty database.
FBTEST:      functional.basic.isql.01
"""

import pytest
from firebird.qa import *

# version: 3.0

substitutions = [('Owner.*', 'Owner'), ('PAGE_SIZE.*', 'PAGE_SIZE'),
                 ('Number of DB pages allocated.*', 'Number of DB pages allocated'),
                 ('Number of DB pages used.*', 'Number of DB pages used'),
                 ('Number of DB pages free.*', 'Number of DB pages free'),
                 ('Sweep.*', 'Sweep'), ('Forced Writes.*', 'Forced Writes'),
                 ('Transaction -.*', ''), ('ODS.*', 'ODS'),
                 ('Wire crypt plugin.*', 'Wire crypt plugin'),
                 ('Creation date.*', 'Creation date'),
                 ('Protocol version.*', 'Protocol version'),
                 ('Default Character.*', 'Default Character')]

db = db_factory()

act = isql_act('db', 'show database;', substitutions=substitutions)

expected_stdout_1 = """
    Database: localhost:test.fdb
    Owner: SYSDBA
    PAGE_SIZE 8192
    Number of DB pages allocated
    Number of DB pages used
    Number of DB pages free
    Sweep interval = 11120000
    Forced Writes are ON
    Transaction - oldest = 1
    Transaction - oldest active = 2
    Transaction - oldest snapshot = 2
    Transaction - Next = 5
    ODS = 12.0
    Database not encrypted
    Creation date: Sep 10, 2021 14:43:52
    Default Character set: NONE
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout_1
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

# version: 4.0

expected_stdout_2 = """
    Database: localhost:test.fdb
    Owner: SYSDBA
    PAGE_SIZE 8192
    Number of DB pages allocated = 212
    Number of DB pages used = 192
    Number of DB pages free = 20
    Sweep interval = 20000
    Forced Writes are ON
    Transaction - oldest = 4
    Transaction - oldest active = 5
    Transaction - oldest snapshot = 5
    Transaction - Next = 9
    ODS = 13.0
    Database not encrypted
    Wire crypt plugin:
    Creation date: Sep 10, 2021 14:43:52
    Protocol version = 17
    Default Character set: NONE
"""

@pytest.mark.version('>=4.0,<5.0')
def test_2(act: Action):
    act.expected_stdout = expected_stdout_2
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

# version: 5.0

expected_stdout_3 = """
    Database: localhost:test.fdb
    Owner: SYSDBA
    PAGE_SIZE 8192
    Number of DB pages allocated = 212
    Number of DB pages used = 192
    Number of DB pages free = 20
    Sweep interval = 20000
    Forced Writes are ON
    Transaction - oldest = 4
    Transaction - oldest active = 5
    Transaction - oldest snapshot = 5
    Transaction - Next = 9
    ODS = 13.0
    Database not encrypted
    Wire crypt plugin:
    Creation date: Sep 10, 2021 7:13:17 GMT
    Protocol version = 17
    Default Character set: NONE
"""

@pytest.mark.version('>=5.0')
def test_3(act: Action):
    act.expected_stdout = expected_stdout_3
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
