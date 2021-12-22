#coding:utf-8
#
# id:           functional.database.alter.01
# title:        Alter database: adding a secondary file
# decription:   Adding a secondary file to the database
# tracker_id:
# min_versions: []
# versions:     1.0
# qmid:

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 1.0
# resources: None

substitutions_1 = [('^.*TEST.G', 'TEST.G'), ('[ ]+', '\t')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# cursor=db_conn.cursor()
#  cursor.execute("ALTER DATABASE ADD FILE '$(DATABASE_LOCATION)TEST.G00' STARTING 10000")
#  db_conn.commit()
#  cursor=db_conn.cursor()
#  cursor.execute("SELECT cast(RDB$FILE_NAME as varchar(150)),RDB$FILE_SEQUENCE,RDB$FILE_START,RDB$FILE_LENGTH  FROM RDB$FILES")
#  printData(cursor)
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
CAST                                                                                                                                                   RDB$FILE_SEQUENCE RDB$FILE_START RDB$FILE_LENGTH
------------------------------------------------------------------------------------------------------------------------------------------------------ ----------------- -------------- ---------------
C:\\JOB\\QA\\FBTEST\\TMP\\TEST.G00                                                                                                                          1                 10000          0
"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action, capsys):
    with act_1.db.connect() as con:
        with con.cursor() as c:
            c.execute(f"ALTER DATABASE ADD FILE '{act_1.db.db_path.with_name('TEST.G00')}' STARTING 10000")
            con.commit()
            c.execute("SELECT cast(RDB$FILE_NAME as varchar(150)),RDB$FILE_SEQUENCE,RDB$FILE_START,RDB$FILE_LENGTH  FROM RDB$FILES")
            act_1.print_data(c)
    # Check
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
