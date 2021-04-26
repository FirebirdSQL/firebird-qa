#coding:utf-8
#
# id:           bugs.core_5862
# title:        Varchar computed column length stores incorrect and invalid values for field
# decription:   
#                  Checked on FB40SS, build 4.0.0.1142: OK, 1.938s.
#                
# tracker_id:   CORE-5862
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test (
        id int
        ,vc_default_user varchar(100) default user
        ,vc_default_literal varchar(100) default 'literal'
        ,vc_generated_explicit varchar(201) computed by (vc_default_user || ' ' || vc_default_literal)
        ,vc_generated_implicit computed by (vc_default_user || ' ' || vc_default_literal) 
    );
    commit;

    set list on;
    select
         rf.rdb$field_name
        ,ff.rdb$field_length
        ,ff.rdb$character_length
    from rdb$relation_fields rf
    join rdb$fields ff on rf.rdb$field_source = ff.rdb$field_name
    where 
        upper(rf.rdb$relation_name) = upper('test') 
        and upper(rf.rdb$field_name) starting with upper('vc_generated_')
    order by rf.rdb$field_position
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$FIELD_NAME                  VC_GENERATED_EXPLICIT

    RDB$FIELD_LENGTH                804
    RDB$CHARACTER_LENGTH            201

    RDB$FIELD_NAME                  VC_GENERATED_IMPLICIT

    RDB$FIELD_LENGTH                804
    RDB$CHARACTER_LENGTH            201
  """

@pytest.mark.version('>=4.0')
def test_core_5862_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

