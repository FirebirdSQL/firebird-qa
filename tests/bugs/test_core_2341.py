#coding:utf-8
#
# id:           bugs.core_2341
# title:        Hidden variables conflict with output parameters, causing assertions, unexpected errors or possibly incorrect results
# decription:   
# tracker_id:   CORE-2341
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  
#  cmd = c.prep("""execute block (i varchar(10) = ?) returns (o varchar(10))
#  as
#  begin
#    o = coalesce(cast(o as date), current_date);
#    o = i;
#    suspend;
#  end""")
#  c.execute(cmd,['asd'])
#  printData(c)
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """O
----------
asd
"""

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_core_2341_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


