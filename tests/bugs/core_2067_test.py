#coding:utf-8
#
# id:           bugs.core_2067
# title:        GROUP by and RDB$DB_KEY problems
# decription:   
# tracker_id:   CORE-2067
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t1 (n integer);
insert into t1 values (1);
insert into t1 values (2);
insert into t1 values (3);
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """-- First problem: it should be invalid to group by n and select rdb$db_key
select n, rdb$db_key from t1 group by n;

-- Second problem: error: column unknown DB_KEY is wrong raised
select n, rdb$db_key from t1 group by 1, 2;

-- Third problem: wrong values for rdb$db_key are returned
select n, t1.rdb$db_key from t1 group by 1, 2;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
           N DB_KEY
============ ================
           1 8000000001000000
           2 8000000002000000
           3 8000000003000000


           N DB_KEY
============ ================
           1 8000000001000000
           2 8000000002000000
           3 8000000003000000
"""
expected_stderr_1 = """Statement failed, SQLSTATE = 42000
Dynamic SQL Error
-SQL error code = -104
-Invalid expression in the select list (not contained in either an aggregate function or the GROUP BY clause)
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

    assert act_1.clean_stdout == act_1.clean_expected_stdout

