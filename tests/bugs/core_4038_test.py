#coding:utf-8
#
# id:           bugs.core_4038
# title:        Broken optimization for the stored dbkeys
# decription:   
# tracker_id:   CORE-4038
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """create table t (dbkey char(8) character set octets);
create index it on t (dbkey);
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLANONLY;
select * from t as t1
  left join t as t2 on t2.dbkey = t1.rdb$db_key;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN JOIN (T1 NATURAL, T2 INDEX (IT))
"""

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

