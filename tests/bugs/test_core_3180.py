#coding:utf-8
#
# id:           bugs.core_3180
# title:        ALTER VIEW with not matched columns in declaration and selection crashs the server
# decription:   
# tracker_id:   CORE-3180
# min_versions: ['2.5.1']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """create view TEST_VIEW (ID) as select 1 from rdb$database;
commit;"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """alter view TEST_VIEW (ID) as select 1, 2 from rdb$database;
COMMIT;
SHOW VIEW TEST_VIEW;



"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\Users\\win7\\Firebird_testsbt-repository	mpugs.core_3180.fdb, User: SYSDBA
SQL> SQL> SQL> ID                              INTEGER Expression
View Source:
==== ======
 select 1 from rdb$database
SQL> SQL> SQL> SQL>"""
expected_stderr_1 = """Statement failed, SQLSTATE = 07002
unsuccessful metadata update
-ALTER VIEW TEST_VIEW failed
-SQL error code = -607
-Invalid command
-number of columns does not match select list
"""

@pytest.mark.version('>=3.0')
def test_core_3180_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

