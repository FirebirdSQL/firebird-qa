#coding:utf-8
#
# id:           bugs.core_3735
# title:        Unprivileged user can delete from RDB$DATABASE, RDB$COLLATIONS, RDB$CHARACTER_SETS
# decription:   
# tracker_id:   CORE-3735
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('-Effective user is.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- See also more complex test in CORE-4731 // Prohibit an ability to issue DML or DDL statements on RDB$ tables
    set wng off;
    create or alter user tmp$c3735 password '123';
    commit;
    revoke all on all from tmp$c3735;
    commit;
    
    connect '$(DSN)' user tmp$c3735 password '123';
    
    --show version;
    
    set list on;
    set blob all;
    select current_user from rdb$database;
    show grants;
    set count on;
    
    --set echo on;
    
    insert into rdb$character_sets(
        rdb$character_set_name
        ,rdb$form_of_use
        ,rdb$number_of_characters
        ,rdb$default_collate_name
        ,rdb$character_set_id
        ,rdb$system_flag
        ,rdb$description
        ,rdb$function_name
        ,rdb$bytes_per_character
    )values (
        'ISO-8859-15',
        null,
        null,
        'ISO-8859-15',
        ( select max(rdb$character_set_id) from rdb$character_sets ) + 1,
        1,
        null,
        null,
        1
    ) returning 
        rdb$character_set_name, 
        rdb$character_set_id, 
        rdb$default_collate_name
    ;
    
    insert into rdb$collations(
        rdb$collation_name
        ,rdb$collation_id
        ,rdb$character_set_id
        ,rdb$collation_attributes
        ,rdb$system_flag
        ,rdb$description
        ,rdb$function_name
        ,rdb$base_collation_name
        ,rdb$specific_attributes
    ) values(
        'SUPER_SMART_ORDER'
        ,( select max(rdb$collation_id) from rdb$collations ) + 1
        ,( select rdb$character_set_id from rdb$character_sets where upper(rdb$character_set_name) = upper('ISO-8859-15')  )
        ,1
        ,1
        ,null
        ,null
        ,null
        ,null
    ) returning 
        rdb$collation_name
        ,rdb$collation_id
        ,rdb$character_set_id
    ;
    
    
    insert into rdb$database(
        rdb$description
        ,rdb$relation_id
        ,rdb$security_class
        ,rdb$character_set_name
    ) values (
        'This is special record, do not delete it!'
       ,( select max(rdb$relation_id) from rdb$relations ) + 1
       ,null
       ,'ISO_HE_HE'
    ) returning
        rdb$description
        ,rdb$relation_id
        ,rdb$security_class
        ,rdb$character_set_name
    ;
    
    
    update rdb$collations set rdb$description = null rows 1 
    returning 
        rdb$collation_id
    ;
    
    update rdb$character_sets set rdb$description = null rows 1 
    returning 
        rdb$character_set_id
    ;
    
    update rdb$database set rdb$character_set_name = 'ISO_HA_HA'
    returning 
        rdb$relation_id
    ;
    
    delete from rdb$collations order by rdb$collation_id desc rows 1
    returning 
        rdb$collation_name
        ,rdb$collation_id
        ,rdb$character_set_id
    ;
    
    delete from rdb$character_sets order by rdb$character_set_id desc rows 1 
    returning 
        rdb$character_set_name, 
        rdb$character_set_id, 
        rdb$default_collate_name
    ;
    
    delete from rdb$database order by rdb$relation_id desc rows 1
    returning
        rdb$description
        ,rdb$relation_id
        ,rdb$security_class
        ,rdb$character_set_name
    ;
    
    commit;
    
    connect '$(DSN)' user sysdba password 'masterkey';
    drop user tmp$c3735;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    USER                            TMP$C3735
  """
expected_stderr_1 = """
    There is no privilege granted in this database
    Statement failed, SQLSTATE = 28000
    no permission for INSERT access to TABLE RDB$CHARACTER_SETS
    Statement failed, SQLSTATE = 28000
    no permission for INSERT access to TABLE RDB$COLLATIONS
    Statement failed, SQLSTATE = 28000
    no permission for INSERT access to TABLE RDB$DATABASE
    Statement failed, SQLSTATE = 28000
    no permission for UPDATE access to TABLE RDB$COLLATIONS
    Statement failed, SQLSTATE = 28000
    no permission for UPDATE access to TABLE RDB$CHARACTER_SETS
    Statement failed, SQLSTATE = 28000
    no permission for UPDATE access to TABLE RDB$DATABASE
    Statement failed, SQLSTATE = 28000
    no permission for DELETE access to TABLE RDB$COLLATIONS
    Statement failed, SQLSTATE = 28000
    no permission for DELETE access to TABLE RDB$CHARACTER_SETS
    Statement failed, SQLSTATE = 28000
    no permission for DELETE access to TABLE RDB$DATABASE
  """

@pytest.mark.version('>=3.0')
def test_core_3735_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

