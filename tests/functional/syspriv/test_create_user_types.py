#coding:utf-8
#
# id:           functional.syspriv.create_user_types
# title:        Check ability to update content of RDB$TYPES.
# decription:   
#                
# tracker_id:   
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('RDB\\$DESCRIPTION.*', 'RDB$DESCRIPTION')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set wng off;
    set list on;
    set count on;

    create or alter view v_check as
    select 
         current_user as who_ami
        ,r.rdb$role_name
        ,rdb$role_in_use(r.rdb$role_name) as RDB_ROLE_IN_USE
        ,r.rdb$system_privileges
    from mon$database m cross join rdb$roles r;
    commit;
    grant select on v_check to public;
    commit;

    create or alter user u01 password '123' revoke admin role;
    revoke all on all from u01;
    commit;

    set term ^;
    execute block as
    begin
      execute statement 'drop role role_for_create_user_types';
      when any do begin end
    end^
    set term ;^
    commit;

    -- Add/change/delete non-system records in RDB$TYPES
    create role role_for_create_user_types set system privileges to CREATE_USER_TYPES;
    commit;
    grant default role_for_create_user_types to user u01;
    commit;

    connect '$(DSN)' user u01 password '123';
    select * from v_check;
    commit;

    --set echo on;

    insert into rdb$types(rdb$field_name, rdb$type, rdb$type_name, rdb$description, rdb$system_flag)
      values( 'amount_avaliable', 
              -32767, 
              'stock_amount', 
              'Total number of units that can be sold immediately to any customer', 
              0 -- rdb$system_flag
            )
    returning rdb$field_name, rdb$type, rdb$type_name, rdb$description, rdb$system_flag
    ;

    insert into rdb$types(rdb$field_name, rdb$type, rdb$type_name, rdb$description, rdb$system_flag)
      values( 'amount_ion_reserve', 
              -2, 
              'stock_amount', 
              'Total number of units that is to be sold for customers who previously did order them', 
              1 -- rdb$system_flag
            );

    update rdb$types set rdb$type = -32768, rdb$field_name = null
    where rdb$type < 0 
    order by rdb$type 
    rows 1
    returning rdb$field_name, rdb$type, rdb$type_name, rdb$description, rdb$system_flag;

    delete from rdb$types where rdb$type < 0
    returning rdb$field_name, rdb$type, rdb$type_name, 
    -- rdb$description, -- TODO: uncomment this after core-5287 will be fixed
    rdb$system_flag
    ;
    commit;

    connect '$(DSN)' user sysdba password 'masterkey';
    drop user u01;
    drop role role_for_create_user_types;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WHO_AMI                         U01
    RDB$ROLE_NAME                   RDB$ADMIN                                                                                                                                                                                                                                                   
    RDB_ROLE_IN_USE                 <false>
    RDB$SYSTEM_PRIVILEGES           FFFFFFFFFFFFFFFF

    WHO_AMI                         U01
    RDB$ROLE_NAME                   ROLE_FOR_CREATE_USER_TYPES                                                                                                                                                                                                                                  
    RDB_ROLE_IN_USE                 <true>
    RDB$SYSTEM_PRIVILEGES           0800000000000000

    Records affected: 2

    RDB$FIELD_NAME                  amount_avaliable                                                                                                                                                                                                                                            
    RDB$TYPE                        -32767
    RDB$TYPE_NAME                   stock_amount                                                                                                                                                                                                                                                
    RDB$DESCRIPTION                 b:782
    Total number of units that can be sold immediately to any customer
    RDB$SYSTEM_FLAG                 0

    Records affected: 0

    RDB$FIELD_NAME                  <null>
    RDB$TYPE                        -32768
    RDB$TYPE_NAME                   stock_amount                                                                                                                                                                                                                                                
    RDB$DESCRIPTION                 b:782
    Total number of units that can be sold immediately to any customer
    RDB$SYSTEM_FLAG                 0


    RDB$FIELD_NAME                  <null>
    RDB$TYPE                        -32768
    RDB$TYPE_NAME                   stock_amount                                                                                                                                                                                                                                                
    RDB$SYSTEM_FLAG                 0
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    INSERT operation is not allowed for system table RDB$TYPES
  """

@pytest.mark.version('>=4.0')
def test_create_user_types_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

