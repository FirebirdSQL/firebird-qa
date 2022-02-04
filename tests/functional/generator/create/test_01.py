#coding:utf-8

"""
ID:          generator.create-01
FBTEST:      functional.generator.create.01
TITLE:       CREATE GENERATOR and query related data from RDB$GENERATORS
DESCRIPTION:
  Run 'CREATE GENERATOR' statement and obtain data about it from system table (rdb$generators).
NOTES:
[07.08.2020]
  we have to separate test for 3.0 and 4.0 because INITIAL value of new sequence
  in FB 4.x now differs from "old good zero" (this is so since CORE-6084 was fixed).

  See also: doc/README.incompatibilities.3to4.txt
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create generator test;
    commit;
    set list on;
    select * from rdb$generators where rdb$generator_name=upper('test');
"""

act = isql_act('db', test_script, substitutions=[('RDB\\$SECURITY_CLASS[ ]+SQL\\$.*', ''), ('RDB\\$GENERATOR_ID.*', '')])

# version: 3.0

expected_stdout_1 = """
    RDB$GENERATOR_NAME              TEST
    RDB$GENERATOR_ID                12
    RDB$SYSTEM_FLAG                 0
    RDB$DESCRIPTION                 <null>
    RDB$SECURITY_CLASS              SQL$366
    RDB$OWNER_NAME                  SYSDBA
    RDB$INITIAL_VALUE               0
    RDB$GENERATOR_INCREMENT         1
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout_1
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

# version: 4.0

expected_stdout_2 = """
    RDB$GENERATOR_NAME              TEST
    RDB$GENERATOR_ID                12
    RDB$SYSTEM_FLAG                 0
    RDB$DESCRIPTION                 <null>
    RDB$SECURITY_CLASS              SQL$366
    RDB$OWNER_NAME                  SYSDBA
    RDB$INITIAL_VALUE               1
    RDB$GENERATOR_INCREMENT         1
"""

@pytest.mark.version('>=4.0')
def test_2(act: Action):
    act.expected_stdout = expected_stdout_2
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
