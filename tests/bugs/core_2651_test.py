#coding:utf-8
#
# id:           bugs.core_2651
# title:        Incorrect "string right truncation" error with NONE column and multibyte connection charset
# decription:   
# tracker_id:   CORE-2651
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """create table TEST_NONE
(VARCHAR_1 VARCHAR(1) CHARACTER SET NONE);

insert into test_none values (ascii_char(1));
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# con = kdb.connect(dsn=dsn,user=user_name,password=user_password,charset='CP943C')
#  c = con.cursor()
#  try:
#      c.execute("select * from TEST_NONE")
#  except:
#      print("Test FAILED")
#  finally:
#      con.close()
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


