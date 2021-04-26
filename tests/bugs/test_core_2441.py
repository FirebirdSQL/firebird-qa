#coding:utf-8
#
# id:           bugs.core_2441
# title:        Server crashes on UPDATE OR INSERT statement
# decription:   
# tracker_id:   CORE-2441
# min_versions: []
# versions:     2.1.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.3
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TABLE_TXT (
    FIELD1 VARCHAR(255)
);
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import datetime
#  c = db_conn.cursor()
#  c.execute("""UPDATE OR INSERT INTO TABLE_TXT (FIELD1)
#  VALUES (CAST(? AS TIMESTAMP))
#  MATCHING(FIELD1)""",[datetime.datetime(2011,5,1)])
#  
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1.3')
@pytest.mark.xfail
def test_core_2441_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


