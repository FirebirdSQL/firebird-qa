#coding:utf-8

"""
ID:          index.alter-04
TITLE:       ALTER INDEX - INACTIVE PRIMARY KEY
DESCRIPTION:
FBTEST:      functional.index.alter.04
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE t( a INTEGER NOT NULL,
                CONSTRAINT pkindx PRIMARY KEY(a)
              );
commit;"""

db = db_factory(init=init_script)

test_script = """ALTER INDEX pkindx INACTIVE;"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 27000
unsuccessful metadata update
-ALTER INDEX PKINDX failed
-action cancelled by trigger (3) to preserve data integrity
-Cannot deactivate index used by a PRIMARY/UNIQUE constraint
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
