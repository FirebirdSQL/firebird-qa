#coding:utf-8
#
# id:           bugs.core_1497
# title:        New builtin function DATEADD() implements wrong choice of keywords for expanded syntax
# decription:
# tracker_id:   CORE-1497
# min_versions: ['2.1.0']
# versions:     2.1.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT DATEADD(1 DAY TO date '29-Feb-2012')
,DATEADD(1 MONTH TO date '29-Feb-2012')
,DATEADD(1 YEAR TO date '29-Feb-2012')
FROM RDB$DATABASE;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\fbtest2\\tmp\\bugs.core_1497.fdb, User: SYSDBA
SQL> CON> CON> CON>
    DATEADD     DATEADD     DATEADD
=========== =========== ===========
2012-03-01  2012-03-29  2013-02-28

SQL>"""

@pytest.mark.version('>=2.1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

