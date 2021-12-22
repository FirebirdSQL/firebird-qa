#coding:utf-8
#
# id:           bugs.core_1798
# title:        RDB$DB_KEY evaluates to NULL in INSERT ... RETURNING
# decription:   
# tracker_id:   
# min_versions: []
# versions:     2.1.1
# qmid:         bugs.core_1798

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.1
# resources: None

substitutions_1 = []

init_script_1 = """create table t (n integer);
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """insert into t values (1) returning rdb$db_key;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
DB_KEY
================
8000000001000000

"""

@pytest.mark.version('>=2.1.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

