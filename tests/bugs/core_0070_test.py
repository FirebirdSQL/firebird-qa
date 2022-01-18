#coding:utf-8

"""
ID:          bugs.core_0070
ISSUE:       394
TITLE:       Expression index regression since 2.0a3
DESCRIPTION:
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table t1 (col1 varchar(36));
    commit;
    insert into t1 select lower(uuid_to_char(gen_uuid())) from rdb$types rows 100;
    commit;
    create index idx1 on t1 computed by (upper(col1));
    commit;

    set planonly;
    select * from t1 where upper(col1) = '1';
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (T1 INDEX (IDX1))
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

