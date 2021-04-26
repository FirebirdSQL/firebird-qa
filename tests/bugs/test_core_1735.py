#coding:utf-8
#
# id:           bugs.core_1735
# title:        Bug in SET DEFAULT statement
# decription:   
# tracker_id:   CORE-1735
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TEST (
   A INTEGER
);
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """ALTER TABLE TEST ADD CHECK (A > 0);

ALTER TABLE TEST ALTER A SET DEFAULT '1000';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.0')
def test_core_1735_1(act_1: Action):
    act_1.execute()

