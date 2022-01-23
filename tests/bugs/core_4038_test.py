#coding:utf-8

"""
ID:          issue-4368
ISSUE:       4368
TITLE:       Broken optimization for the stored dbkeys
DESCRIPTION:
JIRA:        CORE-4038
"""

import pytest
from firebird.qa import *

init_script = """create table t (dbkey char(8) character set octets);
create index it on t (dbkey);
"""

db = db_factory(init=init_script)

test_script = """SET PLANONLY;
select * from t as t1
  left join t as t2 on t2.dbkey = t1.rdb$db_key;
"""

act = isql_act('db', test_script)

expected_stdout = """PLAN JOIN (T1 NATURAL, T2 INDEX (IT))
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

