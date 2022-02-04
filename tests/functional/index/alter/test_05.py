#coding:utf-8

"""
ID:          index.alter-05
TITLE:       ALTER INDEX - INACTIVE FOREIGN KEY
DESCRIPTION:
FBTEST:      functional.index.alter.05
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE pk( a INTEGER NOT NULL,
                CONSTRAINT pkindx PRIMARY KEY(a)
              );
commit;
CREATE TABLE fk( a INTEGER NOT NULL,
                 CONSTRAINT fkindx FOREIGN KEY(a) REFERENCES pk(a)
              );
commit;"""

db = db_factory(init=init_script)

test_script = """ALTER INDEX fkindx INACTIVE;"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 27000
unsuccessful metadata update
-ALTER INDEX FKINDX failed
-action cancelled by trigger (2) to preserve data integrity
-Cannot deactivate index used by an integrity constraint
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
