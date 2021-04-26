#coding:utf-8
#
# id:           bugs.core_3860
# title:        Trace API: Faulty database filter crashes server
# decription:   
#                   Confirmed crash on 2.5.1.26351, got on console:
#                   ===
#                       Unable to complete network request to host "localhost".
#                       -Error reading data from the connection.
#                   ===
#                   For 2.5.x we prepare trace config with invalid pattern for database section, launch trace and do trivial query to some database table.
#                   Trace STDOUT (beside "Trace session ID 5 started") should contain several blocks like this:
#                   ===
#                       Error creating trace session for service manager attachment:
#                       error while parsing trace configuration
#                       	line 8: expected closing element, got "database"
#                   ====
#                   We create array of patterns for each of these messages and search in it each line of trace STDOUT. 
#                   Every line should be found in this patterns array, otherwise this is UNEXPECTED case.
#                   Finally, if every line will be found then we have no unexpected result and 'expected_stdout' should be EMPTY.
#                   Checked on:
#                       2.5.8.27067: OK, 7.000s.
#                       2.5.9.27107: OK, 6.438s.
#                   For 3.0+ we just remain test body empty (there is nothing to check because of changed trace config format).
#                
# tracker_id:   CORE-3860
# min_versions: ['2.5.2']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_core_3860_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


