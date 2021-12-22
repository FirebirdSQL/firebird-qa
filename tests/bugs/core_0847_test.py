#coding:utf-8
#
# id:           bugs.core_0847
# title:        computed field can't be changed to non-computed using 'alter table alter column type xy'
# decription:   
# tracker_id:   CORE-847
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_847

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table t (
      f1 varchar(10),
      f2 varchar(10),
      cf computed by (f1 || ' - ' || f2)
    );
    
    insert into t (f1,f2) values ('0123456789','abcdefghij');
    commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set blob off;
    set list on;
    
    select f1,f2,cf as cf_before_altering from t;
    
    select b.rdb$field_name field_name, cast(a.rdb$computed_source as varchar(80)) computed_source_before_altering
    from rdb$fields a 
    join rdb$relation_fields b  on a.rdb$field_name = b.rdb$field_source
    where b.rdb$field_name = upper('CF');
    
    alter table t alter cf type varchar(30);
    commit;

    select f1,f2,cf as cf_after_altering from t;
    
    select b.rdb$field_name field_name, cast(a.rdb$computed_source as varchar(80)) computed_source_after_altering
    from rdb$fields a 
    join rdb$relation_fields b  on a.rdb$field_name = b.rdb$field_source
    where b.rdb$field_name = upper('CF');
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    F1                              0123456789
    F2                              abcdefghij
    CF_BEFORE_ALTERING              0123456789 - abcdefghij
    
    FIELD_NAME                      CF                                                                                           
    COMPUTED_SOURCE_BEFORE_ALTERING (f1 || ' - ' || f2)
    
    F1                              0123456789
    F2                              abcdefghij
    CF_AFTER_ALTERING               0123456789 - abcdefghij
    
    FIELD_NAME                      CF                                                                                           
    COMPUTED_SOURCE_AFTER_ALTERING  (f1 || ' - ' || f2)
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER TABLE T failed
    -Cannot add or remove COMPUTED from column CF
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

