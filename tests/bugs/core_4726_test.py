#coding:utf-8
#
# id:           bugs.core_4726
# title:        Provide ability to do: REcreate user <user_name> password <user_pwd>
# decription:   
#                   Checked on 4.0.0.1629, CS and SS: OK, 1.788s.
#               
#                   ::: NOTE :::
#                   Clause 'GRANT / REVOKE ADMIN ROLE' must be specified __BEFORE__ 'USING PLUGIN' clause!
#                   Perhaps, documentation need to be corrected.
#                   Sent letter to alex and dimitr, 16.10.2019 20:30.
#                
# tracker_id:   CORE-4726
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' '), ('=', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set width usrname 10;
    set width firstname 10;
    set width sec_plugin 20;
    set width sec_attr_key 20;
    set width sec_attr_val 20;
    set width sec_plugin 20;


    recreate user tmp$c4726 password '123' using plugin Srp;
    recreate user tmp$c4726 password '123' using plugin Srp;
    drop user tmp$c4726 using plugin Srp;
    commit;

    recreate view v_users as
    select
         su.sec$user_name as usrname
        ,su.sec$first_name as firstname
        ,su.sec$plugin as sec_plugin
        ,su.sec$admin as sec_is_admin
        ,su.sec$active as su_active
        ,sa.sec$key as sec_attr_key
        ,sa.sec$value as sec_attr_val
    from sec$users su left 
    join sec$user_attributes sa using(sec$user_name, sec$plugin)
    where su.sec$user_name = upper('TMP$C4726');
    commit;

    -- set echo on;

    ----------------------------- Create Or Alter tests -----------------------------------

    create or alter user tmp$c4726 password '123'
        inactive 
        grant admin role -- 16.10.2019: must be specified BEFORE 'using plugin ...' clause!
        using plugin Srp
        tags (initname='Ozzy', surname='Osbourne', groupname='Black Sabbath', birthday = '03.12.1948')
        -- grant admin role -- 16.10.2019: parsing error if will be here
    ;

    commit;
    select 1 as step, v.* from v_users v;

    create or alter user tmp$c4726 password '123'
        active 
        revoke admin role
        using plugin Srp
        tags (initname='Ian', surname='Gillan', groupname='Deep Purple', drop birthday)
    ;
    commit;
    select 2 as step, v.* from v_users v;

    drop user tmp$c4726 using plugin Srp;
    commit;

    ---------------------------------- REcreate test ---------------------------------------

    recreate user tmp$c4726 password '123'
        inactive 
        grant admin role
        using plugin Srp
        tags (initname='John', surname='Bonham', groupname='Led Zeppelin', birthday = '31.05.1948')
    ;
    commit;
    select 3 as step, v.* from v_users v;

    recreate user tmp$c4726 password '123' active
        revoke admin role
        using plugin Srp
        tags (initname='Roger', surname='Waters', groupname='Pink Floyd', drop birthday)
    ;
    commit;

    select 4 as step, v.* from v_users v;

    drop user tmp$c4726 using plugin Srp;
    commit;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
            STEP USRNAME    FIRSTNAME  SEC_PLUGIN           SEC_IS_ADMIN SU_ACTIVE SEC_ATTR_KEY         SEC_ATTR_VAL         

               1 TMP$C4726  <null>     Srp                  <true>       <false>   BIRTHDAY             03.12.1948           
               1 TMP$C4726  <null>     Srp                  <true>       <false>   GROUPNAME            Black Sabbath        
               1 TMP$C4726  <null>     Srp                  <true>       <false>   INITNAME             Ozzy                 
               1 TMP$C4726  <null>     Srp                  <true>       <false>   SURNAME              Osbourne             


            STEP USRNAME    FIRSTNAME  SEC_PLUGIN           SEC_IS_ADMIN SU_ACTIVE SEC_ATTR_KEY         SEC_ATTR_VAL         

               2 TMP$C4726  <null>     Srp                  <false>      <true>    GROUPNAME            Deep Purple          
               2 TMP$C4726  <null>     Srp                  <false>      <true>    INITNAME             Ian                  
               2 TMP$C4726  <null>     Srp                  <false>      <true>    SURNAME              Gillan               


            STEP USRNAME    FIRSTNAME  SEC_PLUGIN           SEC_IS_ADMIN SU_ACTIVE SEC_ATTR_KEY         SEC_ATTR_VAL         

               3 TMP$C4726  <null>     Srp                  <true>       <false>   BIRTHDAY             31.05.1948           
               3 TMP$C4726  <null>     Srp                  <true>       <false>   GROUPNAME            Led Zeppelin         
               3 TMP$C4726  <null>     Srp                  <true>       <false>   INITNAME             John                 
               3 TMP$C4726  <null>     Srp                  <true>       <false>   SURNAME              Bonham               


            STEP USRNAME    FIRSTNAME  SEC_PLUGIN           SEC_IS_ADMIN SU_ACTIVE SEC_ATTR_KEY         SEC_ATTR_VAL         

               4 TMP$C4726  <null>     Srp                  <false>      <true>    GROUPNAME            Pink Floyd           
               4 TMP$C4726  <null>     Srp                  <false>      <true>    INITNAME             Roger                
               4 TMP$C4726  <null>     Srp                  <false>      <true>    SURNAME              Waters               

  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

