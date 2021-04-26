#coding:utf-8
#
# id:           bugs.core_0967
# title:        SQL with incorrect characters (outside the ASCII range) may be processed wrongly
# decription:   
# tracker_id:   CORE-967
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_967

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """create table t (i integer);
insert into t values (0);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  try:
#    c.execute('update t set i=1'+chr(238)+' where 1=0')
#  except Exception,e:
#    msg = repr(e[0])
#    msg = msg.replace(chr(92),"/")
#    print (msg)
#  else:
#    c.execute('select * from t')
#    printData(c)
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """'Error while preparing SQL statement:/n- SQLCODE: -104/n- Dynamic SQL Error/n- SQL error code = -104/n- Token unknown - line 1, column 17/n- /xee'
"""

@pytest.mark.version('>=2.1')
@pytest.mark.xfail
def test_core_0967_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


