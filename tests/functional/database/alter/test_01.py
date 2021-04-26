#coding:utf-8
#
# id:           functional.database.alter_01
# title:        Alter database: adding a secondary file
# decription:   Adding a secondary file to the database
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

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
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """CAST                                                                                                                                                   RDB$FILE_SEQUENCE RDB$FILE_START RDB$FILE_LENGTH
------------------------------------------------------------------------------------------------------------------------------------------------------ ----------------- -------------- ---------------
C:\\JOB\\QA\\FBTEST\\TMP\\TEST.G00                                                                                                                          1                 10000          0
"""

@pytest.mark.version('>=1.0')
@pytest.mark.xfail
def test_alter_01_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


