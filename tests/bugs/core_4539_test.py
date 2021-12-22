#coding:utf-8
#
# id:           bugs.core_4539
# title:        Server does not accept the right plan
# decription:   
# tracker_id:   CORE-4539
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
    recreate table horse(
        id int primary key
       ,color_id int, name varchar(10)
    );
    recreate table color(
        id int
        ,name varchar(10)
    );
    commit;
    create index color_name on color(name);
    commit;
    
    -------------
    -- Confirmed on WI-T3.0.0.31374 Firebird 3.0 Beta 1
    -- Statement failed, SQLSTATE = 42000
    -- index COLOR_NAME cannot be used in the specified plan
    set planonly;
    select count(*)
    from horse h
    join color c on h.color_id = c.id
    where h.name = c.name
    plan join (h natural, c index (color_name));
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN JOIN (H NATURAL, C INDEX (COLOR_NAME))
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

