#coding:utf-8
#
# id:           bugs.core_6499
# title:        Regression:  can not get statistics for selected table(s) via services, get "found unknown switch" error
# decription:   
#                   Test creates several tables and request statistics for one of them usin Services API.
#                   Output must contain for one and only one (selected) table - TEST_01 (and its index).
#                   All lines from output which do not include this name are ignored (see 'subst' section).
#               
#                   Confirmed bug on 4.0.0.2377, 3.0.8.33420, got:
#                       Unable to perform the requested Service API action:
#                       - SQLCODE: -901
#                       - found unknown switch
#                       -901
#                       336920577
#                   Checked on: 4.0.0.2384, 3.0.8.33424 -- all fine.
#                
# tracker_id:   CORE-6499
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = [('^((?!TEST_01\\s+\\(|TEST_01_ID\\s+\\().)*$', ''), ('TEST_01\\s+\\(.*', 'TEST_01'), ('Index TEST_01_ID\\s+\\(.*', 'Index TEST_01_ID'), ('[ \t]+', ' ')]

init_script_1 = """
    recreate table test_01(id int);
    recreate table test__01(id int);
    recreate table test__011(id int);
    commit;
    insert into test_01 select row_number()over() from rdb$types;
    commit;
    create index test_01_id on test_01(id);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_name=db_conn.database_name
#  db_conn.close()
#  
#  svc = services.connect(host='localhost')
#  # print(svc.get_server_version())
#  svc.get_statistics(database = db_name, show_user_data_pages=1, show_user_index_pages=1, tables = 'TEST_01')
#  info = svc.readlines()
#  svc.wait()
#  for r in info:
#       print(r)
#  svc.close()
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TEST_01 (128)
    Index TEST_01_ID (0)
  """

@pytest.mark.version('>=3.0.8')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


