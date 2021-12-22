#coding:utf-8
#
# id:           bugs.core_2508
# title:        Tricky index names can defeat the parsing logic when generating a human readable plan
# decription:   
#                
# tracker_id:   CORE-2508
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table t(a int not null);
    create index "abc(" on t(a);
    set planonly;
    select * from t where a in (0, 1, 2);
    -- This will produce in 2.5.x:
    -- PLAN (T INDEX (abc(abc(abc())
    --                  ^^^ ^^^
    --                   |   |
    --                   +---+--- NO commas here!
    -- Compare with 3.0:
    -- PLAN (T INDEX (abc(, abc(, abc())
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (T INDEX (abc(, abc(, abc())
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

