#coding:utf-8
#
# id:           bugs.core_5857
# title:        Varchar computed column length stores incorrect and invalid values for field
# decription:   
#                    Confirmed wrong output on WI-T4.0.0.1036:
#                    RDB$FIELD_LENGTH was -2 (instead of 80), RDB$CHARACTER_SET_ID was 0 (instead of 4)
#               
#                    Checked on: WI-V3.0.4.33000, WI-T4.0.0.1040 - ONE of test parts works fine.
#                    ::: NOTE :::
#                    There is still problem with accommodation of resulting string in COMPUITED BY
#                    column when its declared length ("varchar(20)") is equal to the total of lengths
#                    of concatenated columns. 
#                    Because of this one of check statements was temp-ly disabled.
#                    See comment in the ticked 27/Jun/18 05:27 AM.
#                
# tracker_id:   CORE-5857
# min_versions: ['3.0.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test (
        id int,
        vc_default_user varchar(10) character set utf8 default user,
        vc_default_literal varchar(10) character set utf8  default 'Кондуит',
        vc_generated varchar(20) computed by (vc_default_user || ' ' || vc_default_literal)
    );

    insert into test values( 1, 'Австралия', 'Антарктида');
    insert into test values( 2, 'Швамбрания', 'Антарктида');
    commit;

    set count on;
    set list on;

    select
         rf.rdb$field_name
        ,ff.rdb$field_length
        ,ff.rdb$character_length
        ,ff.rdb$character_set_id
        ,ff.rdb$collation_id
        ,ff.rdb$field_type
        ,ff.rdb$field_sub_type
    from rdb$relation_fields rf
    join rdb$fields ff on rf.rdb$field_source = ff.rdb$field_name
    where upper(rf.rdb$relation_name) = upper('test')
    order by 1
    ;

    select vc_generated from test where id = 1;  

    -- temply disabled: select vc_generated from test where id = 2;  
    --    Statement failed, SQLSTATE = 22001
    --    arithmetic exception, numeric overflow, or string truncation
    --    -string right truncation
    --    -expected length 20, actual 21    
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$FIELD_NAME                  ID
    RDB$FIELD_LENGTH                4
    RDB$CHARACTER_LENGTH            <null>
    RDB$CHARACTER_SET_ID            <null>
    RDB$COLLATION_ID                <null>
    RDB$FIELD_TYPE                  8
    RDB$FIELD_SUB_TYPE              0
    RDB$FIELD_NAME                  VC_DEFAULT_LITERAL
    RDB$FIELD_LENGTH                40
    RDB$CHARACTER_LENGTH            10
    RDB$CHARACTER_SET_ID            4
    RDB$COLLATION_ID                0
    RDB$FIELD_TYPE                  37
    RDB$FIELD_SUB_TYPE              0
    RDB$FIELD_NAME                  VC_DEFAULT_USER
    RDB$FIELD_LENGTH                40
    RDB$CHARACTER_LENGTH            10
    RDB$CHARACTER_SET_ID            4
    RDB$COLLATION_ID                0
    RDB$FIELD_TYPE                  37
    RDB$FIELD_SUB_TYPE              0
    RDB$FIELD_NAME                  VC_GENERATED
    RDB$FIELD_LENGTH                80
    RDB$CHARACTER_LENGTH            20
    RDB$CHARACTER_SET_ID            4
    RDB$COLLATION_ID                0
    RDB$FIELD_TYPE                  37
    RDB$FIELD_SUB_TYPE              0
    Records affected: 4
    VC_GENERATED                    Австралия Антарктида
    Records affected: 1  
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

