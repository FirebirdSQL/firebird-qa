#coding:utf-8
#
# id:           functional.intfunc.list.03
# title:        List function with distinct option
# decription:   
# tracker_id:   CORE-964
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.list.list_03

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  c.execute("SELECT RDB$SYSTEM_FLAG, LIST(DISTINCT TRIM(RDB$OWNER_NAME)) FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG=1 GROUP BY 1;")
#  
#  printData(c)
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """RDB$SYSTEM_FLAG LIST
--------------- ----
1               SYSDBA
"""

@pytest.mark.version('>=2.1')
@pytest.mark.xfail
def test_03_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


