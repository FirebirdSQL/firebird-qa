#coding:utf-8

"""
ID:          alter-database-03
TITLE:       Alter database: add file with name of this database or previously added files must fail
DESCRIPTION: Add same file twice must fail
FBTEST:      functional.database.alter.03
"""

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError

db = db_factory()

act = python_act('db')

@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):
    with act.db.connect() as con:
        with con.cursor() as c:
            c.execute(f"ALTER DATABASE ADD FILE '{act.db.db_path.with_name('TEST.G00')}' STARTING 10000")
            con.commit()
            with pytest.raises(DatabaseError, match='.*Cannot add file with the same name as the database or added files.*'):
                c.execute(f"ALTER DATABASE ADD FILE '{act.db.db_path.with_name('TEST.G00')}' STARTING 20000")
    # Passed
