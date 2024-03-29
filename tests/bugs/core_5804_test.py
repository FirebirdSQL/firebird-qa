#coding:utf-8

"""
ID:          issue-6066
ISSUE:       6066
TITLE:       Multiple error in REVOKE operator
DESCRIPTION:
  WARNING-1: test contains two separate sections for executing in 3.0.4+ and 4.0:
  one can NOT use 'DEFAULT' keyword in GRANT/REVOKE role statements.
  Such blocks are commented in 3.0 section.

  WARNING-2: 'SHOW GRANTS' command was replaced with appropriate select from <view> in order to provide stable output.

  Firebird never does any kind of implicit revoke if we use GRANT statement that contains "less" options that previously issued one.
  See additional explanations in the ticket 24/Apr/18 05:06 PM
JIRA:        CORE-5804
FBTEST:      bugs.core_5804
"""

import pytest
from firebird.qa import *

db = db_factory()

# version: 3.0.4

test_script_1 = """
    set bail on;
    set wng off;
    set list on;
    set count on;
    create or alter user tmp$c5804_john password '123';
    commit;

    set term ^;
    create or alter procedure sp_msg (a_msg varchar(100)) returns(msg varchar(100)) as begin
        msg=a_msg;
        suspend;
    end^
    set term ;^
    commit;

    recreate view v_roles as
    select r.*
    from rdb$roles r
    where r.rdb$system_flag is distinct from 1
    ;

    recreate view v_grants as
    select
        p.rdb$user_type       as usr_type
       ,p.rdb$user            as usr_name
       ,p.rdb$grantor         as who_gave
       ,p.rdb$privilege       as what_can
       ,p.rdb$grant_option    as has_grant
       ,p.rdb$object_type     as obj_type
       ,p.rdb$relation_name   as rel_name
       ,p.rdb$field_name      as fld_name
    from rdb$database r left join rdb$user_privileges p on 1=1
    where p.rdb$user in( upper('tmp$c5804_john'), upper('tmp$r5804_boss'), upper('tmp$r5804_acnt') )
    order by 1,2,3,4,5,6,7,8
    ;

    recreate table t(f1 int, f2 int);
    create role tmp$r5804_boss;
    create role tmp$r5804_acnt;
    commit;
    revoke all on all from tmp$c5804_john;
    commit;


    --##################################################################
    --                      G R A N T    O P T I O N
    --##################################################################

    -- check revoke grant option for all table --
    ---------------------------------------------

    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke grant option for update on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked grant option for update of the whole table');
    select v.* from v_grants v;
    commit;

    revoke all on all from tmp$c5804_john;
    commit;

    -- check revoke grant option for the first field --
    ---------------------------------------------------
    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke grant option for update(f1) on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked grant option for update only field F1');
    select v.* from v_grants v;

    commit;
    revoke all on all from tmp$c5804_john;
    commit;

    -- check revoke grant option for the second field --
    ----------------------------------------------------
    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke grant option for update(f2) on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked grant option for update only field F2');
    select v.* from v_grants v;

    revoke all on all from tmp$c5804_john;
    commit;


    -- check revoke grant option for every field --
    -----------------------------------------------
    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke grant option for update(f2, f1) on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked grant option for update of both fields F1 and F2 enumerated as list');
    select v.* from v_grants v;

    revoke all on all from tmp$c5804_john;
    commit;

    --##################################################################
    --                           U P D A T E
    --##################################################################

    -- check revoke update for all table --
    ---------------------------------------
    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke update on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked privilege update for the whole table');
    select v.* from v_grants v; -- no rows should be displayed now!

    revoke all on all from tmp$c5804_john;
    commit;

    -- check revoke update for the first field --
    ---------------------------------------------
    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke update(f1) on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked privilege for update only field F1');
    select v.* from v_grants v; -- only one record with data for field 'F2' should be displayed now

    revoke all on all from tmp$c5804_john;
    commit;

    -- check revoke update the second field --
    ------------------------------------------
    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke update(f2) on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked privilege for update only field F2');
    select v.* from v_grants v; -- only one record with data for field 'F1' should be displayed now

    revoke all on all from tmp$c5804_john;
    commit;


    -- check revoke update for every field --
    -----------------------------------------
    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke update(f1, f2) on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked privilege update of both fields F1 and F2 enumerated as list');
    select v.* from v_grants v; -- no rows should be displayed now

    revoke all on all from tmp$c5804_john;
    commit;



    -- check revoke role --
    -----------------------
    grant tmp$r5804_boss to
    -- role -- allowed only in 4.0
    tmp$r5804_acnt;
    commit;

    -- execute procedure sp_msg('after grant tmp$r5804_boss to role tmp$r5804_acnt');
    -- select v.* from v_grants v;

    revoke tmp$r5804_boss from
    -- role -- allowed only in 4.0
    tmp$r5804_acnt;
    commit;

    -- execute procedure sp_msg('revoked role tmp$r5804_boss from role tmp$r5804_acnt');
    -- select v.* from v_grants v; -- no rows should be displayed now

    --#################################################################
    --             R O L E S :    D E F A U L T    C L A U S E
    --#################################################################

    /*****************************************
    beg of commented block-1

    Following is not allowed in 3.0: 'default' clause can not be used in GRANT / REVOKE role statements

        -- check revoke default of role --
        ----------------------------------
        grant default tmp$r5804_boss
        -- to role -- allowed only in 4.0
        tmp$r5804_acnt; -- ==> rdb$privileges.rdb$field_name = 'D' after this
        commit;

        --execute procedure sp_msg('after grant default tmp$r5804_boss to role tmp$r5804_acnt');
        --select v.* from v_roles v;
        --select v.* from v_grants v;


        execute procedure sp_msg('before revoking only default tmp$r5804_boss from role tmp$r5804_acnt');
        select v.* from v_grants v; -- ==> rdb$privileges.rdb$field_name must be 'D'

        revoke default tmp$r5804_boss from role tmp$r5804_acnt;-- revoke only default option
        commit;

        execute procedure sp_msg('after revoked only default tmp$r5804_boss from role tmp$r5804_acnt');
        select v.* from v_grants v; -- ==> rdb$privileges.rdb$field_name must be NULL

        revoke tmp$r5804_boss from role tmp$r5804_acnt; -- revoke whole role
        commit;



        -- check revoke whole role which was granted with DEFAULT clause --
        -------------------------------------------------------------------
        grant default tmp$r5804_boss to role tmp$r5804_acnt;
        commit;

        revoke tmp$r5804_boss from role tmp$r5804_acnt;
        commit;

        execute procedure sp_msg('after revoked role that was granted with DEFAULT clause');
        select v.* from v_grants v; -- ==> no rows must be displayed now


    end of commented block-1
    ********************************/

    --#################################################################
    --             R O L E S :    A D M I N    C L A U S E
    --#################################################################


    -- check revoke admin option --
    -------------------------------
    grant tmp$r5804_boss to
    -- role -- allowed only in 4.0
    tmp$r5804_acnt with admin option; -- rdb$roles.rdb$grant_option must be 2 after this
    commit;

    execute procedure sp_msg('before revoke admin option from role that was granted with this');
    select v.* from v_grants v;

    revoke admin option for tmp$r5804_boss from
    -- role  -- allowed only in 4.0
    tmp$r5804_acnt; -- rdb$roles.rdb$grant_option must be 0 after this
    commit;

    execute procedure sp_msg('after revoke admin option from role that was granted with this');
    select v.* from v_grants v;

    /*******************************************
    beg of commented block-2

    Following is not allowed in 3.0: 'default' clause can not be used in GRANT / REVOKE role statements

        -- check revoke default from role granted with admin option --
        --------------------------------------------------------------
        grant default tmp$r5804_boss to role tmp$r5804_acnt with admin option;
        commit;

        execute procedure sp_msg('before revoke default tmp$r5804_boss that was granted with admin option to tmp$r5804_acnt');
        select v.* from v_grants v;

        revoke default tmp$r5804_boss from role tmp$r5804_acnt;
        commit;

        execute procedure sp_msg('after revoke default tmp$r5804_boss that was granted with admin option to tmp$r5804_acnt');
        select v.* from v_grants v;

        revoke tmp$r5804_boss from role tmp$r5804_acnt;
        commit;


        -- check revoke admin option from default role --
        -------------------------------------------------
        grant default tmp$r5804_boss to role tmp$r5804_acnt with admin option;
        commit;


        execute procedure sp_msg('before revoke admin option from default role');
        select v.* from v_grants v;

        revoke admin option for tmp$r5804_boss from role tmp$r5804_acnt;
        commit;

        execute procedure sp_msg('after revoke admin option from default role');
        select v.* from v_grants v;

    end of commented block-2
    *******************************************/


    -- added by myself:
    revoke tmp$r5804_boss from
    -- role
    tmp$r5804_acnt;
    commit;



    /*************************************
    beg of commented block-3
    Following is not allowed in 3.0: 'default' clause can not be used in GRANT / REVOKE role statements


        -- check revoke both GO and AO from granted role --
        ---------------------------------------------------
        grant default tmp$r5804_boss to role tmp$r5804_acnt with admin option;
        commit;

        execute procedure sp_msg('before revoke admin option for default role tmp$r5804_boss from role tmp$r5804_acnt');
        select v.* from v_grants v;

        revoke admin option for default tmp$r5804_boss from role tmp$r5804_acnt;
        commit;

        execute procedure sp_msg('after revoke admin option for default role tmp$r5804_boss from role tmp$r5804_acnt');
        select v.* from v_grants v;

        -- me:
        revoke tmp$r5804_boss from role tmp$r5804_acnt;
        commit;

    end of commented block-3
    *********************************/

    -- adding options to role grants --
    -----------------------------------
    drop role tmp$r5804_boss;
    create role tmp$r5804_boss;
    drop role tmp$r5804_acnt;
    create role tmp$r5804_acnt;

    -- commented in 3.0: grant default tmp$r5804_boss to role tmp$r5804_acnt;

    grant tmp$r5804_boss to
    -- role -- allowed in 4.0 only
    tmp$r5804_acnt with admin option;

    commit;
    execute procedure sp_msg('Check aux options: point-1');
    select v.* from v_grants v;

    --~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    recreate table t (i int);
    grant select on t to tmp$c5804_john;
    commit;
    execute procedure sp_msg('Check aux options: point-2a');
    select v.* from v_grants v;

    grant select on t to tmp$c5804_john with grant option;
    commit;
    execute procedure sp_msg('Check aux options: point-2b');
    select v.* from v_grants v;

    grant select on t to tmp$c5804_john;
    commit;
    execute procedure sp_msg('Check aux options: point-2c');
    select v.* from v_grants v; -- must be the same as it was at point-2a

    revoke all on t from tmp$c5804_john;
    revoke tmp$r5804_boss from
    -- role -- allowed in 4.0 only
    tmp$r5804_acnt;
    drop role tmp$r5804_boss;
    drop role tmp$r5804_acnt;
    commit;

    execute procedure sp_msg('Check aux options: point-2d');
    select v.* from v_grants v; -- must be empty

    --~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    create role tmp$r5804_boss;
    create role tmp$r5804_acnt;
    grant tmp$r5804_boss to
    -- role  -- allowed in 4.0 only
    tmp$r5804_acnt;
    commit;
    execute procedure sp_msg('Check aux options: point-3');
    select v.* from v_grants v;


    grant tmp$r5804_boss to
    -- role  -- allowed in 4.0 only
    tmp$r5804_acnt with admin option;
    commit;
    execute procedure sp_msg('Check aux options: point-4');
    select v.* from v_grants v; -- has_grant must be 2


    /*************************************
    beg of commented block-4
    Following is not allowed in 3.0: 'default' clause can not be used in GRANT / REVOKE role statements

        grant default tmp$r5804_boss
        -- to role -- aloowed in 4.0 only
        tmp$r5804_acnt with admin option;
        commit;
        execute procedure sp_msg('Check aux options: point-5');
        select v.* from v_grants v; -- fld_name must be 'D'


        grant default tmp$r5804_boss to role tmp$r5804_acnt;
        commit;
        execute procedure sp_msg('Check aux options: point-6');
        select v.* from v_grants v;

    end of commented block-4
    ***************************************/


    drop role tmp$r5804_boss;
    drop role tmp$r5804_acnt;
    create role tmp$r5804_boss;
    create role tmp$r5804_acnt;
    commit;

    /*************************************
    beg of commented block-5
    Following is not allowed in 3.0: 'default' clause can not be used in GRANT / REVOKE role statements

        grant default tmp$r5804_boss to role tmp$r5804_acnt;
        commit;
        execute procedure sp_msg('Check aux options: point-7');
        select v.* from v_grants v; -- fld_name must be 'D'

    end of commented block-4
    **********************************/

    grant tmp$r5804_boss to
    -- role -- aloowed in 4.0 only
    tmp$r5804_acnt with admin option;
    commit;
    execute procedure sp_msg('Check aux options: point-8');
    select v.* from v_grants v; -- has_grant must be 2


    ---------------------------- final -----------------------------
    commit;
    drop user tmp$c5804_john;
    drop role tmp$r5804_boss;
    drop role tmp$r5804_acnt;
    commit;
"""

act_1 = isql_act('db', test_script_1)

expected_stdout_1 = """
    MSG                             revoked grant option for update of the whole table



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       0
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F1

    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       0
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F2


    Records affected: 2

    MSG                             revoked grant option for update only field F1



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       0
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F1

    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       1
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F2


    Records affected: 2

    MSG                             revoked grant option for update only field F2



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       0
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F2

    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       1
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F1


    Records affected: 2

    MSG                             revoked grant option for update of both fields F1 and F2 enumerated as list



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       0
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F1

    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       0
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F2


    Records affected: 2

    MSG                             revoked privilege update for the whole table


    Records affected: 0

    MSG                             revoked privilege for update only field F1



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       1
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F2


    Records affected: 1

    MSG                             revoked privilege for update only field F2



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       1
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F1


    Records affected: 1

    MSG                             revoked privilege update of both fields F1 and F2 enumerated as list


    Records affected: 0

    MSG                             before revoke admin option from role that was granted with this



    USR_TYPE                        8
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 1

    MSG                             after revoke admin option from role that was granted with this



    USR_TYPE                        8
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       0
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 1

    MSG                             Check aux options: point-1



    USR_TYPE                        8
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 1

    MSG                             Check aux options: point-2a



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        S
    HAS_GRANT                       0
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        <null>

    USR_TYPE                        8
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 2

    MSG                             Check aux options: point-2b



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        S
    HAS_GRANT                       1
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        <null>

    USR_TYPE                        8
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 2

    MSG                             Check aux options: point-2c



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        S
    HAS_GRANT                       1
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        <null>

    USR_TYPE                        8
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 2

    MSG                             Check aux options: point-2d


    Records affected: 0

    MSG                             Check aux options: point-3



    USR_TYPE                        8
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       0
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 1

    MSG                             Check aux options: point-4



    USR_TYPE                        8
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 1

    MSG                             Check aux options: point-8



    USR_TYPE                        8
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 1
"""

@pytest.mark.version('>=3.0.4,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0

test_script_2 = """
    set bail on;
    set wng off;
    set list on;
    set count on;

    create or alter user tmp$c5804_john password '123';
    commit;

    set term ^;
    create or alter procedure sp_msg (a_msg varchar(100)) returns(msg varchar(100)) as begin
        msg=a_msg;
        suspend;
    end^
    set term ;^
    commit;

    recreate view v_roles as
    select r.*
    from rdb$roles r
    where r.rdb$system_flag is distinct from 1
    ;

    recreate view v_grants as
    select
        p.rdb$user_type       as usr_type
       ,p.rdb$user            as usr_name
       ,p.rdb$grantor         as who_gave
       ,p.rdb$privilege       as what_can
       ,p.rdb$grant_option    as has_grant
       ,p.rdb$object_type     as obj_type
       ,p.rdb$relation_name   as rel_name
       ,p.rdb$field_name      as fld_name
    from rdb$database r left join rdb$user_privileges p on 1=1
    where p.rdb$user in( upper('tmp$c5804_john'), upper('tmp$r5804_boss'), upper('tmp$r5804_acnt') )
    order by 1,2,3,4,5,6,7,8
    ;

    recreate table t(f1 int, f2 int);
    create role tmp$r5804_boss;
    create role tmp$r5804_acnt;
    commit;
    revoke all on all from tmp$c5804_john;
    commit;

    --##################################################################
    --                      G R A N T    O P T I O N
    --##################################################################

    -- check revoke grant option for all table --
    ---------------------------------------------

    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke grant option for update on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked grant option for update of the whole table');
    select v.* from v_grants v;
    commit;

    revoke all on all from tmp$c5804_john;
    commit;

    -- check revoke grant option for the first field --
    ---------------------------------------------------
    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke grant option for update(f1) on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked grant option for update only field F1');
    select v.* from v_grants v;

    commit;
    revoke all on all from tmp$c5804_john;
    commit;

    -- check revoke grant option for the second field --
    ----------------------------------------------------
    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke grant option for update(f2) on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked grant option for update only field F2');
    select v.* from v_grants v;

    revoke all on all from tmp$c5804_john;
    commit;


    -- check revoke grant option for every field --
    -----------------------------------------------
    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke grant option for update(f2, f1) on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked grant option for update of both fields F1 and F2 enumerated as list');
    select v.* from v_grants v;

    revoke all on all from tmp$c5804_john;
    commit;


    --##################################################################
    --                           U P D A T E
    --##################################################################

    -- check revoke update for all table --
    ---------------------------------------
    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke update on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked privilege update for the whole table');
    select v.* from v_grants v; -- no rows should be displayed now!

    revoke all on all from tmp$c5804_john;
    commit;

    -- check revoke update for the first field --
    ---------------------------------------------
    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke update(f1) on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked privilege for update only field F1');
    select v.* from v_grants v; -- only one record with data for field 'F2' should be displayed now

    revoke all on all from tmp$c5804_john;
    commit;

    -- check revoke update the second field --
    ------------------------------------------
    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke update(f2) on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked privilege for update only field F2');
    select v.* from v_grants v; -- only one record with data for field 'F1' should be displayed now

    revoke all on all from tmp$c5804_john;
    commit;


    -- check revoke update for every field --
    -----------------------------------------
    grant update(f1, f2) on table t to tmp$c5804_john with grant option;
    commit;

    revoke update(f1, f2) on table t from tmp$c5804_john;
    commit;

    execute procedure sp_msg('revoked privilege update of both fields F1 and F2 enumerated as list');
    select v.* from v_grants v; -- no rows should be displayed now

    revoke all on all from tmp$c5804_john;
    commit;

    --#################################################################
    --             R O L E S :    D E F A U L T    C L A U S E
    --#################################################################


    -- check revoke role --
    -----------------------
    grant tmp$r5804_boss to role tmp$r5804_acnt;
    commit;

    --execute procedure sp_msg('after grant tmp$r5804_boss to role tmp$r5804_acnt');
    --select v.* from v_grants v;

    revoke tmp$r5804_boss from role tmp$r5804_acnt;
    commit;

    -- execute procedure sp_msg('revoked role tmp$r5804_boss from role tmp$r5804_acnt');
    -- select v.* from v_grants v; -- no rows should be displayed now


    -- check revoke default of role --
    ----------------------------------
    grant default tmp$r5804_boss to role tmp$r5804_acnt; -- ==> rdb$privileges.rdb$field_name = 'D' after this
    commit;

    --execute procedure sp_msg('after grant default tmp$r5804_boss to role tmp$r5804_acnt');
    --select v.* from v_roles v;
    --select v.* from v_grants v;


    execute procedure sp_msg('before revoking only default tmp$r5804_boss from role tmp$r5804_acnt');
    select v.* from v_grants v; -- ==> rdb$privileges.rdb$field_name must be 'D'

    revoke default tmp$r5804_boss from role tmp$r5804_acnt;-- revoke only default option
    commit;

    execute procedure sp_msg('after revoked only default tmp$r5804_boss from role tmp$r5804_acnt');
    select v.* from v_grants v; -- ==> rdb$privileges.rdb$field_name must be NULL


    revoke tmp$r5804_boss from role tmp$r5804_acnt;-- revoke whole role
    commit;



    -- check revoke whole role which was granted with DEFAULT clause --
    -------------------------------------------------------------------
    grant default tmp$r5804_boss to role tmp$r5804_acnt;
    commit;

    revoke tmp$r5804_boss from role tmp$r5804_acnt;
    commit;

    execute procedure sp_msg('after revoked role that was granted with DEFAULT clause');
    select v.* from v_grants v; -- ==> no rows must be displayed now


    --#################################################################
    --             R O L E S :    A D M I N    C L A U S E
    --#################################################################


    -- check revoke admin option --
    -------------------------------
    grant tmp$r5804_boss to role tmp$r5804_acnt with admin option; -- rdb$roles.rdb$grant_option must be 2 after this
    commit;

    execute procedure sp_msg('before revoke admin option from role that was granted with this');
    select v.* from v_grants v;

    revoke admin option for tmp$r5804_boss from role tmp$r5804_acnt; -- rdb$roles.rdb$grant_option must be 0 after this
    commit;

    execute procedure sp_msg('after revoke admin option from role that was granted with this');
    select v.* from v_grants v;


    -- check revoke default from role granted with admin option --
    --------------------------------------------------------------
    grant default tmp$r5804_boss to role tmp$r5804_acnt with admin option;
    commit;

    execute procedure sp_msg('before revoke default tmp$r5804_boss that was granted with admin option to tmp$r5804_acnt');
    select v.* from v_grants v;

    revoke default tmp$r5804_boss from role tmp$r5804_acnt;
    commit;

    execute procedure sp_msg('after revoke default tmp$r5804_boss that was granted with admin option to tmp$r5804_acnt');
    select v.* from v_grants v;

    revoke tmp$r5804_boss from role tmp$r5804_acnt;
    commit;



    -- check revoke admin option from default role --
    -------------------------------------------------
    grant default tmp$r5804_boss to role tmp$r5804_acnt with admin option;
    commit;


    execute procedure sp_msg('before revoke admin option from default role');
    select v.* from v_grants v;

    revoke admin option for tmp$r5804_boss from role tmp$r5804_acnt;
    commit;

    execute procedure sp_msg('after revoke admin option from default role');
    select v.* from v_grants v;


    -- me:
    revoke tmp$r5804_boss from role tmp$r5804_acnt;
    commit;

    -- check revoke both GO and AO from granted role --
    ---------------------------------------------------
    grant default tmp$r5804_boss to role tmp$r5804_acnt with admin option;
    commit;

    execute procedure sp_msg('before revoke admin option for default role tmp$r5804_boss from role tmp$r5804_acnt');
    select v.* from v_grants v;

    revoke admin option for default tmp$r5804_boss from role tmp$r5804_acnt;
    commit;

    execute procedure sp_msg('after revoke admin option for default role tmp$r5804_boss from role tmp$r5804_acnt');
    select v.* from v_grants v;

    -- me:
    revoke tmp$r5804_boss from role tmp$r5804_acnt;
    commit;


    -- adding options to role grants --
    -----------------------------------
    drop role tmp$r5804_boss;
    create role tmp$r5804_boss;
    drop role tmp$r5804_acnt;
    create role tmp$r5804_acnt;

    grant default tmp$r5804_boss to role tmp$r5804_acnt;
    grant tmp$r5804_boss to role tmp$r5804_acnt with admin option;

    commit;
    execute procedure sp_msg('Check aux options: point-1');
    select v.* from v_grants v;


    --~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    recreate table t (i int);
    grant select on t to tmp$c5804_john;
    commit;
    execute procedure sp_msg('Check aux options: point-2a');
    select v.* from v_grants v;

    grant select on t to tmp$c5804_john with grant option;
    commit;
    execute procedure sp_msg('Check aux options: point-2b');
    select v.* from v_grants v;

    grant select on t to tmp$c5804_john;
    commit;
    execute procedure sp_msg('Check aux options: point-2c');
    select v.* from v_grants v; -- must be the same as it was at point-2a

    revoke all on t from tmp$c5804_john;
    revoke tmp$r5804_boss from role tmp$r5804_acnt;
    drop role tmp$r5804_boss;
    drop role tmp$r5804_acnt;
    commit;


    execute procedure sp_msg('Check aux options: point-2d');
    select v.* from v_grants v; -- must be empty

    --~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



    create role tmp$r5804_boss;
    create role tmp$r5804_acnt;
    grant tmp$r5804_boss to role tmp$r5804_acnt;
    commit;
    execute procedure sp_msg('Check aux options: point-3');
    select v.* from v_grants v;



    grant tmp$r5804_boss to role tmp$r5804_acnt with admin option;
    commit;
    execute procedure sp_msg('Check aux options: point-4');
    select v.* from v_grants v; -- has_grant must be 2



    grant default tmp$r5804_boss to role tmp$r5804_acnt with admin option;
    commit;
    execute procedure sp_msg('Check aux options: point-5');
    select v.* from v_grants v; -- fld_name must be 'D'


    grant default tmp$r5804_boss to role tmp$r5804_acnt;
    commit;
    execute procedure sp_msg('Check aux options: point-6');
    select v.* from v_grants v;



    drop role tmp$r5804_boss;
    drop role tmp$r5804_acnt;
    create role tmp$r5804_boss;
    create role tmp$r5804_acnt;
    grant default tmp$r5804_boss to role tmp$r5804_acnt;
    commit;
    execute procedure sp_msg('Check aux options: point-7');
    select v.* from v_grants v; -- fld_name must be 'D'



    grant tmp$r5804_boss to role tmp$r5804_acnt with admin option;
    commit;
    execute procedure sp_msg('Check aux options: point-8');
    select v.* from v_grants v; -- has_grant must be 2

    ---------------------------- final -----------------------------
    commit;
    drop user tmp$c5804_john;
    drop role tmp$r5804_boss;
    drop role tmp$r5804_acnt;
    commit;


"""

act_2 = isql_act('db', test_script_2)

expected_stdout_2 = """
    MSG                             revoked grant option for update of the whole table



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       0
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F1

    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       0
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F2


    Records affected: 2

    MSG                             revoked grant option for update only field F1



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       0
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F1

    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       1
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F2


    Records affected: 2

    MSG                             revoked grant option for update only field F2



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       0
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F2

    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       1
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F1


    Records affected: 2

    MSG                             revoked grant option for update of both fields F1 and F2 enumerated as list



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       0
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F1

    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       0
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F2


    Records affected: 2

    MSG                             revoked privilege update for the whole table


    Records affected: 0

    MSG                             revoked privilege for update only field F1



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       1
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F2


    Records affected: 1

    MSG                             revoked privilege for update only field F2



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        U
    HAS_GRANT                       1
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        F1


    Records affected: 1

    MSG                             revoked privilege update of both fields F1 and F2 enumerated as list


    Records affected: 0

    MSG                             before revoking only default tmp$r5804_boss from role tmp$r5804_acnt



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       0
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        D


    Records affected: 1

    MSG                             after revoked only default tmp$r5804_boss from role tmp$r5804_acnt



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       0
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 1

    MSG                             after revoked role that was granted with DEFAULT clause


    Records affected: 0

    MSG                             before revoke admin option from role that was granted with this



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 1

    MSG                             after revoke admin option from role that was granted with this



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       0
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 1

    MSG                             before revoke default tmp$r5804_boss that was granted with admin option to tmp$r5804_acnt



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        D


    Records affected: 1

    MSG                             after revoke default tmp$r5804_boss that was granted with admin option to tmp$r5804_acnt



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 1

    MSG                             before revoke admin option from default role



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        D


    Records affected: 1

    MSG                             after revoke admin option from default role



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       0
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        D


    Records affected: 1

    MSG                             before revoke admin option for default role tmp$r5804_boss from role tmp$r5804_acnt



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        D


    Records affected: 1

    MSG                             after revoke admin option for default role tmp$r5804_boss from role tmp$r5804_acnt



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       0
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 1

    MSG                             Check aux options: point-1



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        D


    Records affected: 1

    MSG                             Check aux options: point-2a



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        S
    HAS_GRANT                       0
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        <null>

    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        D


    Records affected: 2

    MSG                             Check aux options: point-2b



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        S
    HAS_GRANT                       1
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        <null>

    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        D


    Records affected: 2

    MSG                             Check aux options: point-2c



    USR_TYPE                        8
    USR_NAME                        TMP$C5804_JOHN
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        S
    HAS_GRANT                       1
    OBJ_TYPE                        0
    REL_NAME                        T
    FLD_NAME                        <null>

    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        D


    Records affected: 2

    MSG                             Check aux options: point-2d


    Records affected: 0

    MSG                             Check aux options: point-3



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       0
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 1

    MSG                             Check aux options: point-4



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        <null>


    Records affected: 1

    MSG                             Check aux options: point-5



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        D


    Records affected: 1

    MSG                             Check aux options: point-6



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        D


    Records affected: 1

    MSG                             Check aux options: point-7



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       0
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        D


    Records affected: 1

    MSG                             Check aux options: point-8



    USR_TYPE                        13
    USR_NAME                        TMP$R5804_ACNT
    WHO_GAVE                        SYSDBA
    WHAT_CAN                        M
    HAS_GRANT                       2
    OBJ_TYPE                        13
    REL_NAME                        TMP$R5804_BOSS
    FLD_NAME                        D


    Records affected: 1

"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout
