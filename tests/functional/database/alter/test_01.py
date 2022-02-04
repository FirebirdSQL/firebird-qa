#coding:utf-8

"""
ID:          alter-database-01
TITLE:       Alter database: adding a secondary file
DESCRIPTION: Adding a secondary file to the database
FBTEST:      functional.database.alter.01
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db', substitutions=[('^.*TEST.G', 'TEST.G'), ('[ ]+', '\t')])

expected_stdout = """
CAST                                                                                                                                                   RDB$FILE_SEQUENCE RDB$FILE_START RDB$FILE_LENGTH
------------------------------------------------------------------------------------------------------------------------------------------------------ ----------------- -------------- ---------------
C:\\JOB\\QA\\FBTEST\\TMP\\TEST.G00                                                                                                                          1                 10000          0
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):
    with act.db.connect() as con:
        with con.cursor() as c:
            c.execute(f"ALTER DATABASE ADD FILE '{act.db.db_path.with_name('TEST.G00')}' STARTING 10000")
            con.commit()
            c.execute("SELECT cast(RDB$FILE_NAME as varchar(150)),RDB$FILE_SEQUENCE,RDB$FILE_START,RDB$FILE_LENGTH  FROM RDB$FILES")
            act.print_data(c)
    # Check
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
