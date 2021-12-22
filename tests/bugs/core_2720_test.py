#coding:utf-8
#
# id:           bugs.core_2720
# title:        Wrong evaluation result with divide and unary plus\\minus operations
# decription:
# tracker_id:   CORE-2720
# min_versions: ['2.0.6']
# versions:     2.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT 36/4/3, 36/-4/3, 36/+4/3, 36/+-4/3, 36/-+4/3, 36/- -4/3, 36/++4/3 FROM RDB$DATABASE;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\fbtest2\\tmp\\bugs.core_2720.fdb, User: SYSDBA
SQL>
               DIVIDE                DIVIDE                DIVIDE                DIVIDE                DIVIDE                DIVIDE                DIVIDE
===================== ===================== ===================== ===================== ===================== ===================== =====================
                    3                    -3                     3                    -3                    -3                     3                     3

SQL>"""

@pytest.mark.version('>=2.0.6')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

