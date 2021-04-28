#coding:utf-8
#
# id:           functional.basic.isql.01
# title:        ISQL - SHOW DATABASE
# decription:   Check for correct output of SHOW DATABASE on empty database.
# tracker_id:   
# min_versions: ['2.5.2']
# versions:     3.0, 4.0
# qmid:         functional.basic.isql.isql_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('Owner.*', 'Owner'), ('PAGE_SIZE.*', 'PAGE_SIZE'), ('Number of DB pages allocated.*', 'Number of DB pages allocated'), ('Number of DB pages used.*', 'Number of DB pages used'), ('Number of DB pages free.*', 'Number of DB pages free'), ('Sweep.*', 'Sweep'), ('Forced Writes.*', 'Forced Writes'), ('Transaction -.*', ''), ('ODS.*', 'ODS'), ('Default Character.*', 'Default Character')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- 19.01.2016: added line  "Database not encrypted", see  http://sourceforge.net/p/firebird/code/62825
    show database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Database: localhost:c:\\job\\qabtest-repo	mpunctional.basic.isql.isql_01.fdb
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
    Default Character set: NONE
  """

@pytest.mark.version('>=3.0,<4.0')
def test_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = [('Owner.*', 'Owner'), ('PAGE_SIZE.*', 'PAGE_SIZE'), ('Number of DB pages allocated.*', 'Number of DB pages allocated'), ('Number of DB pages used.*', 'Number of DB pages used'), ('Number of DB pages free.*', 'Number of DB pages free'), ('Sweep.*', 'Sweep'), ('Forced Writes.*', 'Forced Writes'), ('Transaction -.*', ''), ('ODS.*', 'ODS'), ('Wire crypt plugin.*', 'Wire crypt plugin'), ('Default Character.*', 'Default Character')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    -- Separate for FB 4.0 since 22.01.2020
    show database;
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    Database: localhost:c:\\job\\qabtest-repo	mpunctional.basic.isql.isql_01.fdb
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
    Default Character set: NONE
  """

@pytest.mark.version('>=4.0')
def test_01_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

