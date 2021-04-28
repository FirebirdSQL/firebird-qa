#coding:utf-8
#
# id:           bugs.core_3365
# title:        Extend syntax for ALTER USER CURRENT_USER
# decription:   
#                   Replaced old code: removed EDS from here as it is not needed at all: 
#                   we can use here trivial "connect '$(DSN)' ..." instead.
#                   Non-privileged user is created in this test and then we check that 
#                   he is able to change his personal data: password, firstname and any of
#                   TAGS key-value pair (avaliable in Srp only).
#               
#                   Checked on 4.0.0.1635: OK, 3.773s; 3.0.5.33180: OK, 2.898s.
#                
# tracker_id:   CORE-3365
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('[ \t]+', ' '), ('=', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bail on;
    set count on;

    -- Drop any old account with name = 'TMP$C3365' if it remains from prevoius run:
    set term ^;
    execute block as
    begin
        begin
            execute statement 'drop user tmp$c3365 using plugin Srp' with autonomous transaction;
            when any do begin end
        end
     
        begin
        execute statement 'drop user tmp$c3365 using plugin Legacy_UserManager' with autonomous transaction;
            when any do begin end
        end
    end^
    set term ;^
    commit;

    set width usrname 10;
    set width firstname 10;
    set width sec_plugin 20;
    set width sec_attr_key 20;
    set width sec_attr_val 20;
    set width sec_plugin 20;

    recreate view v_usr_info as
    select
         su.sec$user_name as usrname
        ,su.sec$first_name as firstname
        ,su.sec$plugin as sec_plugin
        ,sa.sec$key as sec_attr_key
        ,sa.sec$value as sec_attr_val
    from sec$users su left 
    join sec$user_attributes sa using(sec$user_name, sec$plugin)
    where su.sec$user_name = upper('tmp$c3365');
    commit;

    grant select on v_usr_info to public;
    commit;

    create user tmp$c3365 password 'Ir0nM@n' firstname 'John'
        using plugin Srp
        tags (initname='Ozzy', surname='Osbourne', groupname='Black Sabbath', birthday = '03.12.1948')
    ;
    commit;

    select 'before altering' as msg, v.* from v_usr_info v;
    commit;
    
    connect '$(DSN)' user tmp$c3365 password 'Ir0nM@n';

    alter current user 
        set password 'H1ghWaySt@r' firstname 'Ian'
        using plugin Srp
        tags (initname='Ian', surname='Gillan', groupname='Deep Purple', drop birthday)
    ;
    commit;

    connect '$(DSN)' user tmp$c3365 password 'H1ghWaySt@r';
    commit;

    select 'after altering' as msg, v.* from v_usr_info v;
    commit;

    connect '$(DSN)' user SYSDBA password 'masterkey';
    drop user tmp$c3365 using plugin Srp;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG             USRNAME    FIRSTNAME  SEC_PLUGIN           SEC_ATTR_KEY         SEC_ATTR_VAL
    =============== ========== ========== ==================== ==================== ====================
    before altering TMP$C3365  John       Srp                  BIRTHDAY             03.12.1948
    before altering TMP$C3365  John       Srp                  GROUPNAME            Black Sabbath
    before altering TMP$C3365  John       Srp                  INITNAME             Ozzy
    before altering TMP$C3365  John       Srp                  SURNAME              Osbourne
    Records affected: 4

    MSG            USRNAME    FIRSTNAME  SEC_PLUGIN           SEC_ATTR_KEY         SEC_ATTR_VAL
    ============== ========== ========== ==================== ==================== ====================
    after altering TMP$C3365  Ian        Srp                  GROUPNAME            Deep Purple
    after altering TMP$C3365  Ian        Srp                  INITNAME             Ian
    after altering TMP$C3365  Ian        Srp                  SURNAME              Gillan
    Records affected: 3
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

