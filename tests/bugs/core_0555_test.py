#coding:utf-8
#
# id:           bugs.core_555
# title:        Inconsistent results using STARTING WITH and COALESCE
# decription:   
# tracker_id:   CORE-555
# min_versions: []
# versions:     2.0
# qmid:         bugs.core_555

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(name char(31) character set unicode_fss);
    commit;
    insert into test (name) values ('RDB$TRIGGER_1');
    insert into test (name) values ('RDB$TRIGGER_8');
    insert into test (name) values ('RDB$TRIGGER_9');
    insert into test (name) values ('RDB$TRIGGER_2');
    insert into test (name) values ('RDB$TRIGGER_3');
    insert into test (name) values ('RDB$TRIGGER_26');
    insert into test (name) values ('RDB$TRIGGER_25');
    insert into test (name) values ('RDB$TRIGGER_10');
    insert into test (name) values ('RDB$TRIGGER_11');
    insert into test (name) values ('RDB$TRIGGER_12');
    insert into test (name) values ('RDB$TRIGGER_13');
    insert into test (name) values ('RDB$TRIGGER_14');
    insert into test (name) values ('RDB$TRIGGER_15');
    insert into test (name) values ('RDB$TRIGGER_16');
    insert into test (name) values ('RDB$TRIGGER_17');
    insert into test (name) values ('RDB$TRIGGER_18');
    insert into test (name) values ('RDB$TRIGGER_19');
    insert into test (name) values ('RDB$TRIGGER_20');
    insert into test (name) values ('RDB$TRIGGER_21');
    insert into test (name) values ('RDB$TRIGGER_22');
    insert into test (name) values ('RDB$TRIGGER_23');
    insert into test (name) values ('RDB$TRIGGER_24');
    insert into test (name) values ('RDB$TRIGGER_27');
    insert into test (name) values ('RDB$TRIGGER_31');
    insert into test (name) values ('RDB$TRIGGER_32');
    insert into test (name) values ('RDB$TRIGGER_33');
    insert into test (name) values ('RDB$TRIGGER_34');
    insert into test (name) values ('RDB$TRIGGER_35');
    insert into test (name) values ('RDB$TRIGGER_36');
    commit;

    set list on;

    select name "test-1"
    from test a
    where a.name starting with '';
    
    select name "test-2"
    from test a
    where a.name starting with coalesce(null, '');
    
    select name "test-3"
    from test a
    where cast(a.name as char(31)) starting with coalesce(null, '');
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    test-1                          RDB$TRIGGER_1
    test-1                          RDB$TRIGGER_8
    test-1                          RDB$TRIGGER_9
    test-1                          RDB$TRIGGER_2
    test-1                          RDB$TRIGGER_3
    test-1                          RDB$TRIGGER_26
    test-1                          RDB$TRIGGER_25
    test-1                          RDB$TRIGGER_10
    test-1                          RDB$TRIGGER_11
    test-1                          RDB$TRIGGER_12
    test-1                          RDB$TRIGGER_13
    test-1                          RDB$TRIGGER_14
    test-1                          RDB$TRIGGER_15
    test-1                          RDB$TRIGGER_16
    test-1                          RDB$TRIGGER_17
    test-1                          RDB$TRIGGER_18
    test-1                          RDB$TRIGGER_19
    test-1                          RDB$TRIGGER_20
    test-1                          RDB$TRIGGER_21
    test-1                          RDB$TRIGGER_22
    test-1                          RDB$TRIGGER_23
    test-1                          RDB$TRIGGER_24
    test-1                          RDB$TRIGGER_27
    test-1                          RDB$TRIGGER_31
    test-1                          RDB$TRIGGER_32
    test-1                          RDB$TRIGGER_33
    test-1                          RDB$TRIGGER_34
    test-1                          RDB$TRIGGER_35
    test-1                          RDB$TRIGGER_36
    
    test-2                          RDB$TRIGGER_1
    test-2                          RDB$TRIGGER_8
    test-2                          RDB$TRIGGER_9
    test-2                          RDB$TRIGGER_2
    test-2                          RDB$TRIGGER_3
    test-2                          RDB$TRIGGER_26
    test-2                          RDB$TRIGGER_25
    test-2                          RDB$TRIGGER_10
    test-2                          RDB$TRIGGER_11
    test-2                          RDB$TRIGGER_12
    test-2                          RDB$TRIGGER_13
    test-2                          RDB$TRIGGER_14
    test-2                          RDB$TRIGGER_15
    test-2                          RDB$TRIGGER_16
    test-2                          RDB$TRIGGER_17
    test-2                          RDB$TRIGGER_18
    test-2                          RDB$TRIGGER_19
    test-2                          RDB$TRIGGER_20
    test-2                          RDB$TRIGGER_21
    test-2                          RDB$TRIGGER_22
    test-2                          RDB$TRIGGER_23
    test-2                          RDB$TRIGGER_24
    test-2                          RDB$TRIGGER_27
    test-2                          RDB$TRIGGER_31
    test-2                          RDB$TRIGGER_32
    test-2                          RDB$TRIGGER_33
    test-2                          RDB$TRIGGER_34
    test-2                          RDB$TRIGGER_35
    test-2                          RDB$TRIGGER_36
    
    test-3                          RDB$TRIGGER_1
    test-3                          RDB$TRIGGER_8
    test-3                          RDB$TRIGGER_9
    test-3                          RDB$TRIGGER_2
    test-3                          RDB$TRIGGER_3
    test-3                          RDB$TRIGGER_26
    test-3                          RDB$TRIGGER_25
    test-3                          RDB$TRIGGER_10
    test-3                          RDB$TRIGGER_11
    test-3                          RDB$TRIGGER_12
    test-3                          RDB$TRIGGER_13
    test-3                          RDB$TRIGGER_14
    test-3                          RDB$TRIGGER_15
    test-3                          RDB$TRIGGER_16
    test-3                          RDB$TRIGGER_17
    test-3                          RDB$TRIGGER_18
    test-3                          RDB$TRIGGER_19
    test-3                          RDB$TRIGGER_20
    test-3                          RDB$TRIGGER_21
    test-3                          RDB$TRIGGER_22
    test-3                          RDB$TRIGGER_23
    test-3                          RDB$TRIGGER_24
    test-3                          RDB$TRIGGER_27
    test-3                          RDB$TRIGGER_31
    test-3                          RDB$TRIGGER_32
    test-3                          RDB$TRIGGER_33
    test-3                          RDB$TRIGGER_34
    test-3                          RDB$TRIGGER_35
    test-3                          RDB$TRIGGER_36
  """

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

