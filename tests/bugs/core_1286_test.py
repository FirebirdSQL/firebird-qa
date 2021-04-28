#coding:utf-8
#
# id:           bugs.core_1286
# title:        isql: zero divide + coredump when use "-pag 0" command switch & set heading on inside .sql script
# decription:   
# tracker_id:   CORE-1286
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         bugs.core_1286

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """create table test(id int);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# script = """
#      set heading on;
#      select 1 as r from rdb$fields rows 1;
#      -- Crash of ISQL (not server) is reproduced when make connect by ISQL of WI-V2.5.1.26351.
#      -- After ISQL crash firebird.log contains: INET/inet_error: read errno = 10054
#    """
#  runProgram('isql',[dsn,'-pag','0','-user',user_name,'-pas',user_password],script)
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
           R
============
           1
"""

@pytest.mark.version('>=2.5.2')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


