#coding:utf-8
#
# id:           bugs.core_1256
# title:        Table columns hide destination variables of RETURNING INTO
# decription:   
# tracker_id:   CORE-1256
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1256

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """create table t (n integer) ;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """set term ^;

-- ok

execute block returns (n integer)
as
begin
  insert into t values (1) returning n into :n;
  suspend;
end^

-- not ok

execute block returns (n integer)
as
begin
  insert into t values (1) returning n into n;
  suspend;
end^

set term ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
           N
============
           1


           N
============
           1

"""

@pytest.mark.version('>=2.1')
def test_core_1256_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

