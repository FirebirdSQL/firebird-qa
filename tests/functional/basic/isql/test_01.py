#coding:utf-8
#
# id:           functional.basic.isql.01
# title:        ISQL - SHOW DATABASE
# decription:   Check for correct output of SHOW DATABASE on empty database.
# tracker_id:
# min_versions: ['2.5.2']
# versions:     3.0, 4.0, 5.0
# qmid:         functional.basic.isql.isql_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('Owner.*', 'Owner'), ('PAGE_SIZE.*', 'PAGE_SIZE'),
                   ('Number of DB pages allocated.*', 'Number of DB pages allocated'),
                   ('Number of DB pages used.*', 'Number of DB pages used'),
                   ('Number of DB pages free.*', 'Number of DB pages free'),
                   ('Sweep.*', 'Sweep'), ('Forced Writes.*', 'Forced Writes'),
                   ('Transaction -.*', ''), ('ODS.*', 'ODS'),
                   ('Creation date.*', 'Creation date'),
                   ('Default Character.*', 'Default Character')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- 19.01.2016: added line  "Database not encrypted", see  http://sourceforge.net/p/firebird/code/62825
    show database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Database: localhost:c:\\job\\qa\\fbtest-repo\\tmp\\functional.basic.isql.isql_01.fdb
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
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0
# resources: None

substitutions_2 = [('Owner.*', 'Owner'), ('PAGE_SIZE.*', 'PAGE_SIZE'),
                   ('Number of DB pages allocated.*', 'Number of DB pages allocated'),
                   ('Number of DB pages used.*', 'Number of DB pages used'),
                   ('Number of DB pages free.*', 'Number of DB pages free'),
                   ('Sweep.*', 'Sweep'), ('Forced Writes.*', 'Forced Writes'),
                   ('Transaction -.*', ''), ('ODS.*', 'ODS'),
                   ('Wire crypt plugin.*', 'Wire crypt plugin'),
                   ('Creation date.*', 'Creation date'),
                   ('Protocol version.*', 'Protocol version'),
                   ('Default Character.*', 'Default Character')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    -- Separate for FB 4.0 since 22.01.2020
    show database;
"""

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    Database: localhost:c:\\job\\qa\\fbtest-repo\\tmp\\functional.basic.isql.isql_01.fdb
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
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout

# version: 5.0
# resources: None

substitutions_3 = [('Owner.*', 'Owner'), ('PAGE_SIZE.*', 'PAGE_SIZE'),
                   ('Number of DB pages allocated.*', 'Number of DB pages allocated'),
                   ('Number of DB pages used.*', 'Number of DB pages used'),
                   ('Number of DB pages free.*', 'Number of DB pages free'),
                   ('Sweep.*', 'Sweep'), ('Forced Writes.*', 'Forced Writes'),
                   ('Transaction -.*', ''), ('ODS.*', 'ODS'),
                   ('Wire crypt plugin.*', 'Wire crypt plugin'),
                   ('Creation date.*', 'Creation date'),
                   ('Protocol version.*', 'Protocol version'),
                   ('Default Character.*', 'Default Character')]

init_script_3 = """"""

db_3 = db_factory(sql_dialect=3, init=init_script_3)

test_script_3 = """
    -- Separate for FB 5.0 since 10.09.2021
    -- New lines in the output (builds >= 5.0.0.196):
    --     Creation date: Sep 10, 2021 7:13:17 GMT
    --     Protocol version = 17

    show database;
"""

act_3 = isql_act('db_3', test_script_3, substitutions=substitutions_3)

expected_stdout_3 = """
    Database: localhost:c:\\job\\qa\\fbtest-repo\\tmp\\functional.basic.isql.isql_01.fdb
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
def test_3(act_3: Action):
    act_3.expected_stdout = expected_stdout_3
    act_3.execute()
    assert act_3.clean_stdout == act_3.clean_expected_stdout

