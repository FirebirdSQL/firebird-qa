#coding:utf-8
#
# id:           bugs.core_1295
# title:        Bad optimization of queries with DB_KEY
# decription:   
# tracker_id:   CORE-1295
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLANONLY;
select * from rdb$relations where rdb$db_key = ? and rdb$relation_id = 0;
select * from rdb$relations where rdb$db_key = ? and rdb$relation_name = 'RDB$RELATIONS';"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN (RDB$RELATIONS INDEX ())
PLAN (RDB$RELATIONS INDEX ())
"""

@pytest.mark.version('>=2.5.3')
def test_core_1295_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

