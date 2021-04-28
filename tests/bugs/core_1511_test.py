#coding:utf-8
#
# id:           bugs.core_1511
# title:        POSITION(string_exp1, string_exp2 [, start])
# decription:   
# tracker_id:   CORE-1511
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

test_script_1 = """SELECT position ('be', 'To be or not to be')
,position ('be', 'To be or not to be', 4)
,position ('be', 'To be or not to be', 8)
,position ('be', 'To be or not to be', 18)
FROM RDB$DATABASE;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:btest2	mpugs.core_1511.fdb, User: SYSDBA
SQL> CON> CON> CON> CON>
    POSITION     POSITION     POSITION     POSITION
============ ============ ============ ============
           4            4           17            0

SQL>"""

@pytest.mark.version('>=2.1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

