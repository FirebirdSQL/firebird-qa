#coding:utf-8
#
# id:           bugs.core_3902
# title:        Derived fields may not be optimized via an index
# decription:   
# tracker_id:   CORE-3902
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
select rdb$database.rdb$relation_id from rdb$database
  left outer join
  ( select rdb$relations.rdb$relation_id as tempid
    from rdb$relations ) temp (tempid)
  on temp.tempid = rdb$database.rdb$relation_id;
select rdb$database.rdb$relation_id from rdb$database
  left outer join
  ( select rdb$relations.rdb$relation_id
    from rdb$relations ) temp
  on temp.rdb$relation_id = rdb$database.rdb$relation_id;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """SQL>
PLAN JOIN (RDB$DATABASE NATURAL, TEMP RDB$RELATIONS INDEX (RDB$INDEX_1))
SQL>
PLAN JOIN (RDB$DATABASE NATURAL, TEMP RDB$RELATIONS INDEX (RDB$INDEX_1))
SQL>"""

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

