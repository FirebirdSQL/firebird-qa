#coding:utf-8
#
# id:           bugs.core_5068
# title:        gbak with invalid parameter crashes FB
# decription:   
#                  Confirmed crash on 2.5.5.26952, but only when use 'gbak' utility (with services call).
#                  As of fbsvcmgr, it works correct and reports error: Unknown switch "res_user_all_space".
#                  Output when use gbak is:
#                  gbak:unknown switch "USER_ALL_SPACE"
#                  gbak: ERROR:Unable to complete network request to host "localhost".
#                  gbak: ERROR:    Error reading data from the connection.
#                  gbak:Exiting before completion due to errors
#               
#                  Checked on WI-V2.5.6.26962 -  works OK.
#                  No test needed for 3.0 thus only stub code present here in 'firebird_version': '3.0' section.
#                
# tracker_id:   CORE-5068
# min_versions: ['2.5.5']
# versions:     3.0
# qmid:         

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
def test_core_5068_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


